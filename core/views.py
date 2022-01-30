from typing import Any, Dict, Optional

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse  # NOQA
from django.http.response import HttpResponseBase
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView

from .models import Attempt, Hunt, Puzzle, Round, SaltedAnswer, Solution, TestSolveSession, Token, Unlockable, get_viewable  # NOQA


class StaffRequiredMixin(PermissionRequiredMixin):
	permission_required = 'is_staff'


class GeneralizedSingleObjectMixin(SingleObjectMixin[Model]):
	def get_object(self, queryset: QuerySet[Any] = None):
		kwargs = self.kwargs  # type: ignore
		if queryset is None:
			queryset = self.get_queryset()
		for keyword in kwargs:
			if kwargs[keyword] == '-':
				kwargs.pop(keyword)
				kwargs[keyword + '__isnull'] = True
		return queryset.get(**kwargs)


Context = Dict[str, Any]


def get_token_from_request(request: HttpRequest) -> Optional[Token]:
	uuid = request.COOKIES.get('uuid', None)

	if request.user.is_authenticated and uuid is not None:
		# first get the attached token
		try:
			user_token: Optional[Token] = Token.objects.get(user=request.user, enabled=True)
		except Token.DoesNotExist:
			user_token = None
		try:
			uuid_token: Optional[Token] = Token.objects.get(uuid=uuid, enabled=True)
		except Token.DoesNotExist:
			uuid_token = None
		if user_token is None and uuid_token is None:
			return None
		elif user_token is None and uuid_token is not None:
			return uuid_token
		elif user_token is not None and uuid_token is None:
			return user_token
		elif user_token is not None and uuid_token is not None and user_token.pk == uuid_token.pk:
			return user_token  # either one okay
		else:
			return user_token
	elif uuid is not None:  # no authentication
		try:
			return Token.objects.get(uuid=uuid, enabled=True)
		except Token.DoesNotExist:
			return None
	elif request.user.is_authenticated:  # no cookie
		try:
			return Token.objects.get(user=request.user, enabled=True)
		except Token.DoesNotExist:
			return None
	else:
		return None


class HuntList(ListView):
	"""Top-level list of all the hunts"""
	context_object_name = "hunt_list"
	model = Hunt

	def get_queryset(self):
		return Hunt.objects.filter(visible=True)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['token'] = get_token_from_request(self.request)
		return context


class RoundUnlockableList(ListView):
	"""List of all the top-level rounds in a given hunt"""
	context_object_name = "round_unlockable_list"
	template_name = "core/round_unlockable_list.html"
	model = Unlockable

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		context['hunt'] = self.hunt
		return context

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
		self.hunt = Hunt.objects.get(volume_number=self.kwargs['volume_number'])
		self.token = get_token_from_request(self.request)
		if not self.hunt.has_started:
			if self.token is None or self.token.is_plebian:
				return render(request, "core/too_early.html", {'hunt': self.hunt, 'token': self.token})
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self) -> QuerySet[Unlockable]:
		queryset = Unlockable.objects.filter(
			hunt=self.hunt, parent__isnull=True
		).select_related('round')
		if self.hunt.active is True:
			if self.token is None:
				raise PermissionDenied
			return get_viewable(queryset, self.token)
		return queryset


class UnlockableList(ListView):
	"""List of all the unlockables in a given round"""
	context_object_name = "unlockable_list"
	model = Unlockable

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
		self.cheating = self.kwargs.pop('cheating', False)
		self.round = Round.objects.get(**self.kwargs)
		self.hunt = self.round.unlockable.hunt
		self.token = get_token_from_request(request)

		if self.token is None:
			if self.hunt.has_ended:
				return super().dispatch(request, *args, **kwargs)
			else:
				raise PermissionDenied()
		elif not self.token.has_unlocked(self.round.unlockable):
			return HttpResponseRedirect(self.round.unlockable.get_absolute_url())
		else:
			return super().dispatch(request, *args, **kwargs)

	def get_queryset(self) -> QuerySet[Unlockable]:
		if self.token is None:
			if self.hunt.has_ended:
				return Unlockable.objects.filter(parent=self.round)
			else:
				raise PermissionDenied()
		else:
			assert self.round.unlockable is None or self.token.can_unlock(self.round.unlockable)
			queryset: QuerySet[Unlockable] = Unlockable.objects.filter(parent=self.round)
			if self.cheating is True and self.round.unlockable is not None:
				assert self.round.unlockable.hunt.allow_cheat(self.token)
			else:
				queryset = get_viewable(queryset, self.token)
			queryset = queryset.annotate(round_exists=Count('round'))
			queryset = queryset.order_by(
				'sort_order',
				'name',
			)
			queryset = queryset.select_related('puzzle', 'round')
			return queryset

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		context['round'] = self.round
		context['cheating'] = self.cheating
		return context


class PuzzleDetail(DetailView):
	"""Shows a puzzle"""
	model = Puzzle
	context_object_name = "puzzle"

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		return context

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
		self.token = get_token_from_request(self.request)
		if self.token is not None:
			u = self.object.unlockable  # type: ignore
			if u.hunt.active is True:
				assert self.token.has_unlocked(u)
		return super().dispatch(request, *args, **kwargs)


class PuzzleDetailTestSolve(DetailView, GeneralizedSingleObjectMixin):
	"""Shows a puzzle, no questions asked"""
	model = Puzzle
	context_object_name = "puzzle"

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		return context

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
		self.token = get_token_from_request(request)
		if self.token is None or self.token.is_plebian:
			raise PermissionDenied()
		session = TestSolveSession.objects.get(uuid=self.kwargs['testsolvesession__uuid'])
		assert session.expires > timezone.now()
		return super().dispatch(request, *args, **kwargs)


class PuzzleSolutionDetail(DetailView):
	"""Shows a solution"""
	model = Puzzle
	context_object_name = "puzzle"
	template_name = 'core/puzzlesolution_detail.html'

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		return context

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
		self.cheating = kwargs.pop('cheating', False)
		self.token = get_token_from_request(self.token)
		u = self.object.unlockable  # type: ignore
		if u.hunt.active is True:
			assert self.token is not None
			if self.cheating is True:
				attempt, _ = Attempt.objects.get_or_create(unlockable=u, token=self.token)
				if attempt.status != 1:
					attempt.status = 1
					attempt.save()
			else:
				assert self.token.has_solved(u)
		return super().dispatch(request, *args, **kwargs)


class UnlockableDetail(DetailView):
	model = Unlockable
	context_object_name = "unlockable"

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		token = get_token_from_request(self.request)
		context['token'] = token
		u = self.object  # type: ignore
		if token is not None:
			can_unlock = token.can_unlock(u)
			attempt, _ = Attempt.objects.get_or_create(unlockable=u, token=token)
			context['locked'] = not can_unlock
			context['new'] = attempt.status < 0 and can_unlock
			if can_unlock and u.story_only is True and attempt.status < 1:
				attempt.status = 1
				attempt.save()
			elif can_unlock and attempt.status < 0:
				attempt.status = 0
				attempt.save()
		elif u.hunt.has_ended:
			context['locked'] = False
			context['new'] = False
		else:
			raise PermissionDenied()
		return context


class TokenDetailView(DetailView[Token]):
	model = Token
	context_object_name = "token"


class TokenUpdateView(UpdateView[Token, BaseModelForm[Token]]):
	model = Token
	context_object_name = "token"
	fields = ('name', )


def token_disable(uuid: str) -> HttpResponse:
	token = Token.objects.get(uuid=uuid)
	token.enabled = False
	token.user = None
	token.save()
	return HttpResponseRedirect('/')


@csrf_exempt
def ajax(request: HttpRequest) -> JsonResponse:
	if request.method != 'POST':
		return JsonResponse({'error': "☕"}, status=418)

	token: Optional[Token]
	try:
		assert 'uuid' in request.COOKIES
		token = Token.objects.get(uuid=request.COOKIES['uuid'], enabled=True)
	except Token.DoesNotExist:
		token = None
	except AssertionError:
		token = None

	action = request.POST.get('action')
	if action == 'guess':
		puzzle = Puzzle.objects.get(slug=request.POST.get('puzzle_slug'))
		guess = request.POST.get('guess') or ''
		salt = int(request.POST.get('salt') or 0)
		sa = SaltedAnswer.objects.get(puzzle=puzzle, salt=salt)
		if not sa.equals(guess):
			return JsonResponse({'correct': 0})
		elif sa.is_correct:
			if puzzle.unlockable is not None and token is not None:
				Attempt.objects.filter(token=token, unlockable=puzzle.unlockable).update(status=1)
			return JsonResponse({
				'correct': 1,
				'url': puzzle.get_solution_url(),
			})
		else:
			return JsonResponse({'correct': 0.5, 'message': sa.message})

	elif action == 'log':
		raise NotImplementedError('TODO log')

	elif action == 'get_token':
		name = request.POST['name']
		reduced_name = Token.reduce(name)
		force_new = request.POST['force_new']
		if force_new == 'false' and Token.objects.filter(
			reduced_name=reduced_name, user__isnull=False
		).exists():
			return JsonResponse({'outcome': 'exists'})
		else:
			token = Token(name=name)
			token.save()
			return JsonResponse({
				'outcome': 'success',
				'uuid': token.uuid,
			})

	return JsonResponse({'message': f'No such method {action}'}, status=400)


# -- Staff views --


class PuzzleUpdate(UpdateView[Puzzle, BaseModelForm[Puzzle]], StaffRequiredMixin):
	model = Puzzle
	context_object_name = "puzzle"
	fields = (
		'name',
		'slug',
		'status_progress',
		'flavor_text',
		'content',
		'puzzle_head',
	)


class SolutionUpdate(
	UpdateView[Solution, BaseModelForm[Solution]], StaffRequiredMixin,
	GeneralizedSingleObjectMixin
):
	model = Solution
	context_object_name = "solution"
	fields = (
		'post_solve_story',
		'solution_text',
		'author_notes',
		'post_solve_image_path',
		'post_solve_image_path',
	)


class RoundUpdate(
	UpdateView[Round, BaseModelForm[Round]], StaffRequiredMixin, GeneralizedSingleObjectMixin
):
	model = Round
	context_object_name = "round"
	fields = (
		'name', 'chapter_number', 'show_chapter_number', 'slug', 'thumbnail_path', 'round_text'
	)


class UnlockableUpdate(
	UpdateView[Unlockable, BaseModelForm[Unlockable]], StaffRequiredMixin,
	GeneralizedSingleObjectMixin
):
	model = Unlockable
	context_object_name = "unlockable"
	fields = (
		'name', 'slug', 'story_only', 'intro_story_text', 'force_visibility', 'courage_bounty'
	)


class StaffHuntList(ListView, StaffRequiredMixin):
	"""Staff view of all the hunts"""
	context_object_name = "hunt_list"
	model = Hunt
	redirect_if_no_token = False
	template_name = 'core/staff_hunt_list.html'

	def get_queryset(self):
		return Hunt.objects.order_by('-start_date')


class StaffPuzzleList(ListView, StaffRequiredMixin):
	"""Staff list of the puzzles"""
	context_object_name = "puzzle_list"
	model = Puzzle
	redirect_if_no_token = False
	template_name = 'core/staff_puzzle_list.html'

	def get_queryset(self):
		return Puzzle.objects.filter(
			status_progress__range=(0, 6)
		).order_by('status_progress').select_related('unlockable', 'solution')


class StaffUnlockableList(ListView, StaffRequiredMixin):
	"""Staff list of unlockables"""
	context_object_name = "unlockable_list"
	model = Unlockable
	redirect_if_no_token = False
	template_name = 'core/staff_unlockable_list.html'

	def get_queryset(self):
		self.hunt = Hunt.objects.get(**self.kwargs)
		return Unlockable.objects.filter(hunt=self.hunt).order_by('sort_order')

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['hunt'] = self.hunt
		return context
