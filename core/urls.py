from django.urls import path

from . import views

urlpatterns = [
	path(r'', views.HuntList.as_view(), name='hunt-list'),
	path(r'puzzle/<str:slug>', views.PuzzleView.as_view(), name='puzzle-view'),
	path(r'chapter/<str:slug>', views.PuzzleList.as_view(), name='puzzle-list'),
	path(r'volume/<int:number>', views.RoundList.as_view(), name='round-list'),
	]
