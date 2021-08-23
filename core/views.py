from typing import Any, Dict, Optional

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse  # NOQA
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView

from .models import Attempt, Hunt, Puzzle, Round, SaltedAnswer, Solution, TestSolveSession, Token, Unlockable, get_viewable  # NOQA


class StaffRequiredMixin(PermissionRequiredMixin):
	permission_required = 'is_staff'


class GeneralizedSingleObjectMixin(SingleObjectMixin):
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


class TokenGatedView:
	redirect_if_no_token = True
	token = None

	def check_token(self, request: HttpRequest):
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
				self.token = None
			elif user_token is None and uuid_token is not None:
				self.token = uuid_token
			elif user_token is not None and uuid_token is None:
				self.token = user_token
			elif user_token is not None and uuid_token is not None and user_token.pk == uuid_token.pk:
				self.token = user_token  # either one okay
			else:
				# oh god multiple accounts
				self.token = user_token
		elif uuid is not None:  # no authentication
			try:
				self.token = Token.objects.get(uuid=uuid, enabled=True)
			except Token.DoesNotExist:
				self.token = None
		elif request.user.is_authenticated:  # no cookie
			try:
				self.token = Token.objects.get(user=request.user, enabled=True)
			except Token.DoesNotExist:
				self.token = None
		else:
			self.token = None

		if self.token is None and self.redirect_if_no_token:
			return HttpResponseRedirect(reverse_lazy('hunt-list'))
		return None


# vvv amazing code, so much for DRY
# maybe i should take paul graham's advice and switch to lisp
class TokenGatedListView(TokenGatedView, ListView):
	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
		return super().check_token(request) or super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		return context


class TokenGatedDetailView(TokenGatedView, DetailView):
	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
		return super().check_token(request) or super().dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		return context


class HuntList(TokenGatedListView):
	"""Top-level list of all the hunts"""
	context_object_name = "hunt_list"
	model = Hunt
	redirect_if_no_token = False

	def get_queryset(self):
		return Hunt.objects.filter(visible=True)


class RoundUnlockableList(TokenGatedListView):
	"""List of all the top-level rounds in a given hunt"""
	context_object_name = "round_unlockable_list"
	template_name = "core/round_unlockable_list.html"
	model = Unlockable

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
		ret = super().dispatch(request, *args, **kwargs)
		if not self.hunt.has_started and (self.token is None or self.token.is_plebian):
			return render(request, "core/too_early.html", {'hunt': self.hunt, 'token': self.token})
		return ret

	def get_queryset(self) -> QuerySet[Unlockable]:
		self.cheating = self.kwargs.pop('cheating', False)
		self.hunt = Hunt.objects.get(**self.kwargs)
		queryset = Unlockable.objects.filter(hunt=self.hunt,
			parent__isnull=True).select_related('round')
		assert self.token is not None
		if self.cheating is True:
			assert self.hunt.allow_cheat(self.token)
		else:
			queryset = get_viewable(queryset, self.token)
		return queryset

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['hunt'] = self.hunt
		context['cheating'] = self.cheating
		return context


class UnlockableList(TokenGatedListView):
	"""List of all the unlockables in a given round"""
	context_object_name = "unlockable_list"
	model = Unlockable

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
		self.cheating = self.kwargs.pop('cheating', False)
		r = super().check_token(request)
		if r is not None:
			return r
		self.round = Round.objects.get(**self.kwargs)
		if self.token is not None and self.round.unlockable is not None and not self.token.has_unlocked(
			self.round.unlockable
		):
			return HttpResponseRedirect(self.round.unlockable.get_absolute_url())
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self) -> QuerySet[Unlockable]:
		assert self.token is not None
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
		context['round'] = self.round
		context['cheating'] = self.cheating
		return context


class PuzzleDetail(TokenGatedDetailView):
	"""Shows a puzzle"""
	model = Puzzle
	context_object_name = "puzzle"

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
		ret = super().dispatch(request, *args, **kwargs)
		assert self.token is not None
		u = self.object.unlockable  # type: ignore
		assert self.token.has_unlocked(u)
		return ret


class PuzzleDetailTestSolve(TokenGatedDetailView, GeneralizedSingleObjectMixin):
	"""Shows a puzzle, no questions asked"""
	model = Puzzle
	context_object_name = "puzzle"

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
		ret = super().dispatch(request, *args, **kwargs)
		if self.token is None:
			return HttpResponseRedirect(reverse_lazy('hunt-list'))
		session = TestSolveSession.objects.get(uuid=self.kwargs['testsolvesession__uuid'])
		assert session.expires > timezone.now()
		assert not self.token.is_plebian, "not an authorized testsolver"
		return ret

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['is_testsolve_session'] = True
		return context


class PuzzleSolutionDetail(TokenGatedDetailView):
	"""Shows a solution"""
	model = Puzzle
	context_object_name = "puzzle"
	template_name = 'core/puzzlesolution_detail.html'

	def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
		self.cheating = kwargs.pop('cheating', False)
		ret = super().dispatch(request, *args, **kwargs)
		assert self.token is not None
		u = self.object.unlockable  # type: ignore
		if self.cheating is True:
			assert u.hunt.allow_cheat(self.token), "can't cheat yet"
			attempt, _ = Attempt.objects.get_or_create(unlockable=u, token=self.token)
			if attempt.status != 1:
				attempt.status = 1
				attempt.save()
		else:
			assert self.token.has_solved(u)
		return ret

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		context['cheating'] = self.cheating
		return context


class UnlockableDetail(TokenGatedDetailView):
	model = Unlockable
	context_object_name = "unlockable"

	def get_context_data(self, **kwargs: Any) -> Context:
		context = super().get_context_data(**kwargs)
		token = context['token']
		u = self.object  # type: ignore
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
		return context


class TokenDetailView(DetailView):
	model = Token
	context_object_name = "token"


class TokenUpdateView(UpdateView):
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


class PuzzleUpdate(UpdateView, StaffRequiredMixin):
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


class SolutionUpdate(UpdateView, StaffRequiredMixin, GeneralizedSingleObjectMixin):
	model = Solution
	context_object_name = "solution"
	fields = (
		'post_solve_story',
		'solution_text',
		'author_notes',
		'post_solve_image_path',
		'post_solve_image_path',
	)


class RoundUpdate(UpdateView, StaffRequiredMixin, GeneralizedSingleObjectMixin):
	model = Round
	context_object_name = "round"
	fields = (
		'name', 'chapter_number', 'show_chapter_number', 'slug', 'thumbnail_path', 'round_text'
	)


class UnlockableUpdate(UpdateView, StaffRequiredMixin, GeneralizedSingleObjectMixin):
	model = Unlockable
	context_object_name = "unlockable"
	fields = (
		'name', 'slug', 'story_only', 'intro_story_text', 'force_visibility', 'courage_bounty'
	)


class StaffHuntList(TokenGatedListView, StaffRequiredMixin):
	"""Staff view of all the hunts"""
	context_object_name = "hunt_list"
	model = Hunt
	redirect_if_no_token = False
	template_name = 'core/staff_hunt_list.html'

	def get_queryset(self):
		return Hunt.objects.order_by('-start_date')


class StaffPuzzleList(TokenGatedListView, StaffRequiredMixin):
	"""Staff list of the puzzles"""
	context_object_name = "puzzle_list"
	model = Puzzle
	redirect_if_no_token = False
	template_name = 'core/staff_puzzle_list.html'

	def get_queryset(self):
		return Puzzle.objects.filter(
				status_progress__range=(0,6))\
				.order_by('status_progress').select_related('unlockable', 'solution')

class StaffUnlockableList(TokenGatedListView, StaffRequiredMixin):
	"""Staff list of unlockables"""
	context_object_name = "unlockable_list"
	model = Unlockable
	redirect_if_no_token = False
	template_name = 'core/staff_unlockable_list.html'
	def get_queryset(self):
		self.hunt = models.Hunt.objects.get(**self.kwargs)
		return models.Unlockable.objects.filter(hunt = self.hunt).order_by('sort_order')
	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		context['hunt'] = self.hunt
		return context
