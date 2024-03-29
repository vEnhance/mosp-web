from django.urls import path

from . import views

urlpatterns = [
    path(r"", views.HuntList.as_view(), name="hunt-list"),
    # -- puzzle --
    path(
        r"<str:unlockable__hunt__volume_number>/puzzle/<str:slug>",
        views.PuzzleDetail.as_view(),
        name="puzzle-detail",
    ),
    path(
        r"<str:unlockable__hunt__volume_number>/solution/<str:slug>",
        views.PuzzleSolutionDetail.as_view(),
        name="solution-detail",
    ),
    # -- chapter --
    path(
        r"chapter/<str:chapter_number>",
        views.UnlockableList.as_view(),
        name="unlockable-list",
    ),
    # -- volume --
    path(
        r"volume/<str:volume_number>",
        views.RoundUnlockableList.as_view(),
        name="round-unlockable-list",
    ),
    # -- edit --
    path(
        r"<str:unlockable__hunt__volume_number>/puzzle/<str:slug>/edit",
        views.PuzzleUpdate.as_view(),
        name="puzzle-update",
    ),
    path(
        r"<str:puzzle__unlockable__hunt__volume_number>/solution/<str:puzzle__slug>/edit",
        views.SolutionUpdate.as_view(),
        name="solution-update",
    ),
    path(
        r"<str:hunt__volume_number>/unlockable/<str:slug>/edit",
        views.UnlockableUpdate.as_view(),
        name="unlockable-update",
    ),
    path(
        r"chapter/<str:chapter_number>/edit",
        views.RoundUpdate.as_view(),
        name="round-update",
    ),
    # -- staff --
    path(r"staff/hunts", views.StaffHuntList.as_view(), name="staff-hunt-list"),
    path(r"staff/puzzles", views.StaffPuzzleList.as_view(), name="staff-puzzle-list"),
    path(
        r"staff/unlockables/<str:volume_number>",
        views.StaffUnlockableList.as_view(),
        name="staff-unlockable-list",
    ),
    # -- other --
    path(
        r"<str:hunt__volume_number>/unlock/<str:slug>",
        views.UnlockableDetail.as_view(),
        name="unlockable-detail",
    ),
    path(r"ajax", views.ajax, name="ajax"),
]
