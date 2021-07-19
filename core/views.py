from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from typing import Any, Dict, Optional
from . import models

Context = Dict[str, Any]

class TokenGatedView:
	redirect_if_no_token = True
	token = None
	def check_token(self, request : HttpRequest):
		uuid = request.COOKIES.get('uuid', None)
		print(uuid)
		if uuid is not None:
			try:
				self.token = models.Token.objects.get(uuid=uuid, enabled=True)
			except models.Token.DoesNotExist:
				self.token = None
			if request.user.is_authenticated:
				try:
					old_token = models.Token.objects.get(user = request.user, enabled = True)
					if self.token is None:
						self.token = old_token
				except models.Token.DoesNotExist:
					if self.token is not None:
						self.token.user = request.user
						self.token.save()

		elif request.user.is_authenticated:
			try:
				self.token = models.Token.objects.get(user = request.user, enabled=True)
				return None
			except models.Token.DoesNotExist:
				pass
		else:
			self.token = None
		if self.token is None and self.redirect_if_no_token:
			return HttpResponseRedirect(reverse_lazy('hunt-list'))
		return None

# vvv amazing code, so much for DRY
# maybe i should take paul graham's advice and switch to lisp
class TokenGatedListView(TokenGatedView, ListView):
	def dispatch(self, request : HttpRequest, *args, **kwargs):
		return super().check_token(request) or \
				super().dispatch(request, *args, **kwargs)
	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		return context
class TokenGatedDetailView(TokenGatedView, DetailView):
	def dispatch(self, request : HttpRequest, *args, **kwargs):
		return super().check_token(request) or \
				super().dispatch(request, *args, **kwargs)
	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		context['token'] = self.token
		return context

class HuntList(TokenGatedListView):
	"""Top-level list of all the hunts"""
	context_object_name = "hunt_list"
	model = models.Hunt
	redirect_if_no_token = False
	def get_queryset(self):
		return models.Hunt.objects.filter(visible = True)

class RoundUnlockableList(TokenGatedListView):
	"""List of all the top-level rounds in a given hunt"""
	context_object_name = "round_unlockable_list"
	template_name = "core/round_unlockable_list.html"
	model = models.Unlockable
	def get_queryset(self):
		cheating = self.kwargs.pop('cheating')
		self.hunt = models.Hunt.objects.get(**self.kwargs)
		queryset = models.Unlockable.objects.filter(
				hunt = self.hunt,
				parent__isnull = True).select_related('round')
		assert self.token is not None
		if cheating is True:
			assert self.hunt.allow_cheat(self.token)
		else:
			queryset = models.get_viewable(queryset, self.token)
		return queryset
	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		context['hunt'] = self.hunt
		return context

class UnlockableList(TokenGatedListView):
	"""List of all the unlockables in a given round"""
	context_object_name = "unlockable_list"
	model = models.Unlockable
	def get_queryset(self):
		cheating = self.kwargs.pop('cheating')
		self.round = models.Round.objects.get(**self.kwargs)
		assert self.token is not None
		assert self.token.has_unlocked(self.round.unlockable)
		queryset = models.Unlockable.objects.filter(
				parent = self.round.unlockable)
		if cheating is True:
			assert self.round.unlockable.hunt.allow_cheat(self.token)
		else:
			queryset = models.get_viewable(queryset, self.token)
		queryset = queryset.annotate(round_exists=Count('round'))
		return queryset.select_related('puzzle', 'round')
	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		context['round'] = self.round
		return context

class PuzzleDetail(TokenGatedDetailView):
	"""Shows a puzzle"""
	model = models.Puzzle
	context_object_name = "puzzle"
	def dispatch(self, request : HttpRequest, *args, **kwargs):
		ret = super().dispatch(request, *args, **kwargs)
		assert self.token is not None
		u = self.object.unlockable # type: ignore
		assert self.token.has_unlocked(u)
		return ret

class SolutionDetail(TokenGatedDetailView):
	"""Shows a solution"""
	model = models.Puzzle
	context_object_name = "puzzle"
	template_name = 'core/solution_detail.html'
	def dispatch(self, request : HttpRequest, *args, **kwargs):
		ret = super().dispatch(request, *args, **kwargs)
		assert self.token is not None
		u = self.object.unlockable # type: ignore
		assert self.token.has_solved(u)
		return ret

class UnlockableDetail(TokenGatedDetailView):
	model = models.Unlockable
	context_object_name = "unlockable"

	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		token = context['token']
		u = self.object # type: ignore
		can_unlock = token.can_unlock(u)
		attempt, _ = models.Attempt.objects.get_or_create(
						unlockable = u, token = token
						)
		context['locked'] = not can_unlock
		context['new'] = attempt.status < 0
		if can_unlock and u.story_only is True and attempt.status < 1:
			attempt.status = 1
			attempt.save()
		elif can_unlock and attempt.status < 0:
			attempt.status = 0
		return context

class TokenDetailView(DetailView):
	model = models.Token
	context_object_name = "token"

class TokenUpdateView(UpdateView):
	model = models.Token
	context_object_name = "token"
	fields = ('name', )

def token_disable(uuid) -> HttpResponse:
	token = models.Token.objects.get(uuid=uuid)
	token.enabled = False
	token.user = None
	token.save()
	return HttpResponseRedirect('/')

@csrf_exempt
def ajax(request) -> JsonResponse:
	if request.method != 'POST':
		return JsonResponse({'error' : "☕"}, status = 418)

	token : Optional[models.Token]
	try:
		assert 'uuid' in request.COOKIES
		token = models.Token.objects.get(
				uuid=request.COOKIES['uuid'],
				enabled=True
				)
	except models.Token.DoesNotExist:
		token = None
	except AssertionError:
		token = None

	action = request.POST.get('action')
	if action == 'guess':
		puzzle = models.Puzzle.objects.get(slug = request.POST.get('puzzle_slug'))
		guess = request.POST.get('guess')
		salt = request.POST.get('salt')
		sa = models.SaltedAnswer.objects.get(puzzle = puzzle, salt = salt)
		if not sa.equals(guess):
			return JsonResponse({'correct' : 0})
		elif sa.is_final:
			models.Attempt.objects.filter(
					token=token, unlockable=puzzle.unlockable
					).update(status=1)
			return JsonResponse({
				'correct' : 1,
				'url' : reverse_lazy('solution-detail', args=(puzzle.slug,)),
				})
		else:
			return JsonResponse({'correct' : 0.5, 'message' : sa.message})

	elif action == 'log':
		raise NotImplementedError('TODO log')

	elif action == 'get_token':
		name = request.POST['name']
		reduced_name = models.Token.reduce(name)
		force_new = request.POST['force_new']
		if force_new == 'false' and models.Token.objects.filter(
				reduced_name = reduced_name,
				user__isnull = False
				).exists():
			return JsonResponse({'outcome' : 'exists'})
		else:
			token = models.Token(name = name)
			token.save()
			return JsonResponse({
				'outcome': 'success',
				'uuid' : token.uuid,
				})

	return JsonResponse({'message' :
		f'No such method {action}'}, status=400)
