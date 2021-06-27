# from django.shortcuts import render
from django.views.generic import ListView
from . import models

# Create your views here.

class HuntList(ListView):
	context_object_name = "hunt_list"
	model = models.Hunt
