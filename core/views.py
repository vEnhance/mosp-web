from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from typing import Any, Dict, Optional
import random

from . import models
from .colormap import big_color_list

Context = Dict[str, Any]

# vvv amazing code, so much for DRY
# maybe i should take paul graham's advice and switch to lisp

class TokenGatedView:
	redirect_if_no_token = True
	token = None
	def check_token(self, request : HttpRequest):
		uuid = request.COOKIES.get('uuid', None)
		if not uuid:
			self.token = None
		else:
			try:
				self.token = models.Token.objects.get(uuid=uuid, enabled=True)
			except models.Token.DoesNotExist:
				self.token = None
		if self.token is None and self.redirect_if_no_token:
			return HttpResponseRedirect(reverse_lazy('hunt-list'))
		return None

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
		self.hunt = models.Hunt.objects.get(**self.kwargs)
		queryset = models.Unlockable.objects.filter(
				hunt = self.hunt,
				parent__isnull = True).select_related('round')
		assert self.token is not None
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
		self.round = models.Round.objects.get(**self.kwargs)
		assert self.token is not None
		assert self.token.has_unlocked(self.round.unlockable)
		return models.get_viewable(
				models.Unlockable.objects.filter(
					parent = self.round.unlockable
				), self.token)\
				.select_related('puzzle', 'round')\
				.order_by('puzzle__is_meta',
						'puzzle__name', 'round__name', )
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
		is_prev_unlocked = (attempt.status >= 0)
		if is_prev_unlocked is False and can_unlock:
			attempt.status = 0
			attempt.save()
		context['locked'] = not can_unlock
		context['new'] = not is_prev_unlocked
		return context


class TokenDetailView(DetailView):
	model = models.Token
	context_object_name = "token"

class TokenUpdateView(UpdateView):
	model = models.Token
	context_object_name = "token"
	fields = ('name', 'passphrase',)

def token_disable(uuid) -> HttpResponse:
	token = models.Token.objects.get(uuid=uuid)
	token.enabled = False
	token.save()
	return HttpResponseRedirect('/')

@csrf_exempt
def ajax(request) -> JsonResponse:
	if request.method != 'POST':
		return JsonResponse({'error' : "☕"}, status = 418)

	token : Optional[models.Token]
	try:
		assert 'uuid' in request.COOKIES
		token = models.Token.objects.get(uuid=request.COOKIES['uuid'],
				enabled=True)
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
		passphrase = request.POST['passphrase']
		if passphrase != '':
			try:
				token = models.Token.objects.get(
						reduced_name = models.Token.reduce(name),
						reduced_passphrase = models.Token.reduce(passphrase),
						enabled = True)
			except models.Token.DoesNotExist:
				return JsonResponse({'outcome' : 'wrong'})
			else:
				return JsonResponse({
					'outcome' : 'success',
					'uuid' : token.uuid,
					'new' : False,
					})
		elif force_new == 'false' and models.Token.objects.filter(
				reduced_name = reduced_name
				).exists():
			return JsonResponse({'outcome' : 'exists'})
		else:
			hexcode, tone, colorname = \
					random.choice(big_color_list)
			token = models.Token.objects.create(
					name = name,
					passphrase = colorname,
					)
			return JsonResponse({
				'outcome': 'success',
				'uuid' : token.uuid,
				'new' : True,
				'hexcode' : hexcode,
				'tone' : tone,
				'colorname' : colorname,
				})

	return JsonResponse({'message' :
		f'No such method {action}'}, status=400)
