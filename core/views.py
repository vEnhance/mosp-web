from django.shortcuts import render
from django.views.generic import ListView
from django.http import HttpRequest, parse_cookie
from . import models
from http.cookies import SimpleCookie

# Create your views here.

# it seems that we want to create a cookie for each person
# and then store the progress on the database end?
# i don't know how this would work to be honest lol

class HuntList(ListView):
	context_object_name = "hunt_list"
	model = models.Hunt

def unlock_puzzle(
		hunt_number : int,
		place_slug : str,
		request : HttpRequest,
		):
	puzzle = models.Puzzle.objects.get(
			hunt = hunt_number,
			place_slug = place_slug
			)
	cookies = parse_cookie(request.COOKIES)
	pass
