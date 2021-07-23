from django.urls import path

from . import views

urlpatterns = [
	path(r'', views.HuntList.as_view(), name='hunt-list'),
	# -- puzzle --
	path(r'puzzle/<str:slug>',
		views.PuzzleDetail.as_view(),
		name='puzzle-detail'),
	path(r'solution/<str:slug>',
		views.SolutionDetail.as_view(),
		kwargs={'cheating':False},
		name='solution-detail'),
	path(r'solution/<str:slug>/spoil',
		views.SolutionDetail.as_view(),
		kwargs={'cheating':True},
		name='solution-detail-cheating'),
	# -- chapter --
	path(r'chapter/<str:chapter_number>',
		views.UnlockableList.as_view(),
		kwargs={'cheating' : False},
		name='unlockable-list'),
	path(r'chapter/<str:chapter_number>/spoil',
		views.UnlockableList.as_view(),
		kwargs={'cheating' : True},
		name='unlockable-list-cheating'),
	# -- volume --
	path(r'volume/<str:volume_number>',
		views.RoundUnlockableList.as_view(),
		kwargs={'cheating' : False},
		name='round-unlockable-list'),
	path(r'volume/<str:volume_number>/spoil',
		views.RoundUnlockableList.as_view(),
		kwargs={'cheating' : True},
		name='round-unlockable-list-cheating'),
	# -- edit --
	path(r'puzzle/<str:slug>/edit',
		views.PuzzleUpdate.as_view(),
		name='puzzle-update'),
	# -- other --
	path(r'unlock/<str:slug>',
		views.UnlockableDetail.as_view(),
		name='unlockable-detail'),
	path(r'profile/<str:pk>',
		views.TokenDetailView.as_view(),
		name='token-detail'),
	path(r'update/<str:pk>',
		views.TokenUpdateView.as_view(),
		name='token-update'),
	path(r'destroy/<str:pk>',
		views.token_disable,
		name='token-disable'),
	path(r'ajax',
		views.ajax,
		name='ajax'),
	]
