from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponseRedirect
from django.forms import ModelForm
from . import models
from typing import Any, Dict
Context = Dict[str, Any]

class SetNameForm(ModelForm):
	class Meta:
		model = models.Token
		fields = ('name',)

# vvv amazing code, so much for DRY
# maybe i should take paul graham's advice and switch to lisp
class TokenGatedListView(ListView):
	def dispatch(self, request : HttpRequest, *args, **kwargs):
		uuid = self.request.COOKIES.get('uuid', None)
		if not uuid:
			return HttpResponseRedirect(reverse_lazy('hunt-list'))
		return super().dispatch(request, *args, **kwargs)
	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		if 'uuid' in self.request.COOKIES:
			context['token'] = models.Token.objects.get(uuid=self.request.COOKIES['uuid'])
		return context
class TokenGatedDetailView(DetailView):
	def dispatch(self, request : HttpRequest, *args, **kwargs):
		uuid = self.request.COOKIES.get('uuid', None)
		if not uuid:
			return HttpResponseRedirect(reverse_lazy('hunt-list'))
		return super().dispatch(request, *args, **kwargs)
	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		if 'uuid' in self.request.COOKIES:
			context['token'] = models.Token.objects.get(uuid=self.request.COOKIES['uuid'])
		return context

class HuntList(TokenGatedListView):
	"""Top-level list of all the hunts"""
	context_object_name = "hunt_list"
	model = models.Hunt
	def dispatch(self, request : HttpRequest, *args, **kwargs):
		if request.method == 'POST':
			form = SetNameForm(request.POST)
			if form.is_valid():
				token = form.save()
				response = self.get(request, *args, **kwargs)
				response.set_cookie(key = 'uuid', value = token.uuid)
				return response
		else:
			form = SetNameForm()
		if 'uuid' not in request.COOKIES:
			return render(request, 'core/welcome.html', {'form' : form})
		else:
			return self.get(request, *args, **kwargs)

class RoundList(TokenGatedListView):
	"""List of all the rounds in a given hunt"""
	context_object_name = "round_list"
	template_name = "core/round_list.html"
	model = models.Round
	def get_queryset(self):
		self.hunt = models.Hunt.objects.get(**self.kwargs)
		return models.Round.objects.filter(unlockable__hunt = self.hunt)
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
		return models.Unlockable.objects.filter(parent = self.round.unlockable)
	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		context['round'] = self.round
		return context

class PuzzleDetail(TokenGatedDetailView):
	"""Shows a puzzle"""
	model = models.Puzzle
	context_object_name = "puzzle"

class SolutionDetail(TokenGatedDetailView):
	"""Shows a solution"""
	model = models.Puzzle
	context_object_name = "puzzle"
	template_name = "core/solution_detail.html"

class UnlockableDetail(TokenGatedDetailView):
	model = models.Unlockable
	context_object_name = "unlockable"

	def get_context_data(self, **kwargs) -> Context:
		context = super().get_context_data(**kwargs)
		token = context['token']
		u = self.object # type: ignore
		can_unlock = token.can_unlock(u)
		is_prev_unlocked = models.Solve.objects.filter(
						unlockable = u, token = token
						).exists()
		if is_prev_unlocked is False and can_unlock:
			models.Solve(unlockable=u, token=token).save()
		context['locked'] = not can_unlock
		context['new'] = not is_prev_unlocked
		return context
