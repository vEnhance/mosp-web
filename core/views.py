from django.db.models.deletion import SET
from django.shortcuts import render
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponseRedirect
from django.forms import ModelForm
from . import models

# Create your views here.

# it seems that we want to create a cookie for each person
# and then store the progress on the database end?
# i don't know how this would work to be honest lol

class SetNameForm(ModelForm):
	class Meta:
		model = models.Token
		fields = ('name',)

class HuntList(ListView):
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
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if 'uuid' in self.request.COOKIES:
			context['token'] = models.Token.objects.get(uuid=self.request.COOKIES['uuid'])
		return context

def unlock_puzzle(
		hunt_number : int,
		place_slug : str,
		request : HttpRequest,
		):
	puzzle = models.Puzzle.objects.get(
			hunt = hunt_number,
			place_slug = place_slug
			)
