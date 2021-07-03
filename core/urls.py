from django.urls import path

from . import views

urlpatterns = [
	path(r'', views.HuntList.as_view(), name='hunt-list'),
	path(r'puzzle/<str:slug>', views.PuzzleDetail.as_view(), name='puzzle-detail'),
	path(r'chapter/<str:chapter_number>', views.UnlockableList.as_view(), name='unlockable-list'),
	path(r'volume/<str:volume_number>', views.RoundList.as_view(), name='round-list'),
	path(r'world/<str:slug>', views.UnlockableDetail.as_view(), name='unlockable-detail'),
	]
