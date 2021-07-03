from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponseRedirect
from django.forms import ModelForm
from . import models

# Create your views here.

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
	def get_context_data(self, **kwargs):
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
	def get_context_data(self, **kwargs):
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
	model = models.Puzzle
	def get_queryset(self):
		current_hunt = models.Hunt.objects.get(
				pk = self.kwargs['pk']
				)
		return models.Puzzle.rounds.filter(
				hunt = current_hunt
				)

class PuzzleList(TokenGatedListView):
	"""List of all the puzzles in a given round"""
	context_object_name = "round_list"
	model = models.Puzzle
	def get_queryset(self):
		current_round = models.Puzzle.rounds.get(
				pk = self.kwargs['pk']
				)
		return models.Puzzle.puzzles.filter(
				parent = current_round
				)

class PuzzleView(TokenGatedDetailView):
	"""Shows a puzzle"""
	model = models.Puzzle

