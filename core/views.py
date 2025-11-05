from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, JsonResponse  # NOQA
from django.http.response import HttpResponseBase
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView

from core.progresso import (
    check_unlocked,
    get_solved_pks,
    mark_opened,
    mark_solved,
    set_courage,
)

from .models import Hunt, Puzzle, Round, SaltedAnswer, Solution, Unlockable  # NOQA
from .utils import is_staff


class StaffRequiredMixin(PermissionRequiredMixin):
    permission_required = "is_staff"


class GeneralizedSingleObjectMixin(SingleObjectMixin[Any]):
    def get_object(self, queryset: QuerySet[Any] = None):
        kwargs = self.kwargs  # type: ignore
        if queryset is None:
            queryset = self.get_queryset()
        for keyword in kwargs:
            if kwargs[keyword] == "-":
                kwargs.pop(keyword)
                kwargs[keyword + "__isnull"] = True
        return queryset.get(**kwargs)


Context = Dict[str, Any]


class HuntList(ListView[Hunt]):
    """Top-level list of all the hunts"""

    context_object_name = "hunt_list"
    model = Hunt

    def get_queryset(self):
        return Hunt.objects.filter(visible=True)


class RoundUnlockableList(ListView[Unlockable]):
    """List of all the top-level rounds in a given hunt"""

    context_object_name = "round_unlockable_list"
    template_name = "core/round_unlockable_list.html"
    model = Unlockable

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["hunt"] = self.hunt
        return context

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        set_courage(request)
        self.hunt = Hunt.objects.get(volume_number=self.kwargs["volume_number"])
        if not self.hunt.has_started and not is_staff(request.user):
            return render(request, "core/too_early.html", {"hunt": self.hunt})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Unlockable]:
        return Unlockable.objects.filter(
            hunt=self.hunt, parent__isnull=True
        ).select_related("round")


class UnlockableList(ListView[Unlockable]):
    """List of all the unlockables in a given round"""

    context_object_name = "unlockable_list"
    model = Unlockable
    object: Unlockable

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        set_courage(request)
        self.round = Round.objects.get(**self.kwargs)
        assert self.round.unlockable is not None
        self.hunt = self.round.unlockable.hunt
        if not check_unlocked(request, self.round.unlockable):
            raise PermissionDenied("Not unlocked yet")
        mark_opened(request, self.round.unlockable)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Unlockable]:
        queryset = Unlockable.objects.filter(parent=self.round)
        queryset = queryset.annotate(round_exists=Count("round"))
        queryset = queryset.order_by(
            "sort_order",
            "name",
        )
        queryset = queryset.select_related("puzzle", "round")
        return queryset

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        context["round"] = self.round
        return context


class PuzzleDetail(DetailView[Puzzle]):
    """Shows a puzzle"""

    model = Puzzle
    context_object_name = "puzzle"
    object: Puzzle

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        set_courage(self.request)
        ret = super().dispatch(request, *args, **kwargs)
        if not check_unlocked(request, self.object.unlockable):
            if is_staff(request.user):
                messages.warning(
                    request, "Viewing as staff. You don't have this unlocked yet."
                )
            else:
                raise PermissionDenied("This puzzle cannot be unlocked yet")
        else:
            mark_opened(request, self.object.unlockable)
        return ret


class PuzzleSolutionDetail(DetailView[Puzzle]):
    """Shows a solution"""

    model = Puzzle
    context_object_name = "puzzle"
    template_name = "core/puzzlesolution_detail.html"
    object: Puzzle

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        set_courage(self.request)
        ret = super().dispatch(request, *args, **kwargs)
        u = self.object.unlockable
        if not check_unlocked(request, u):
            if is_staff(request.user):
                messages.warning(
                    request, "Viewing as staff. You don't have this unlocked yet."
                )
            else:
                raise PermissionDenied("This puzzle cannot be unlocked yet")
        if u.hunt.active and self.object.unlockable.pk not in get_solved_pks(request):
            if is_staff(request.user):
                messages.warning(
                    request, "Viewing as staff. You haven't solved this yet."
                )
            else:
                raise PermissionDenied("This puzzle has not been solved yet.")
        return ret


class UnlockableDetail(DetailView[Unlockable]):
    model = Unlockable
    context_object_name = "unlockable"
    object: Unlockable

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        context["locked"] = not check_unlocked(self.request, self.object)
        return context

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        ret = super().dispatch(request, *args, **kwargs)
        hunt = self.object.hunt
        if not hunt.has_started or not hunt.visible:
            raise PermissionDenied("This unlockable cannot be unlocked yet")
        set_courage(self.request)
        return ret


@csrf_exempt
def ajax(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "☕"}, status=418)

    action = request.POST.get("action")
    print(action)
    if action == "guess":
        puzzle = Puzzle.objects.get(slug=request.POST.get("puzzle_slug"))
        guess = request.POST.get("guess") or ""
        salt = int(request.POST.get("salt") or 0)
        sa = SaltedAnswer.objects.get(puzzle=puzzle, salt=salt)
        print(sa)
        print(guess)
        print(request.session["solved"])
        if not sa.equals(guess):
            return JsonResponse({"correct": 0})
        elif sa.is_correct:
            mark_solved(request, puzzle.unlockable)
            print(request.session)
            return JsonResponse(
                {
                    "correct": 1,
                    "url": puzzle.get_solution_url(),
                }
            )
        else:
            return JsonResponse({"correct": 0.5, "message": sa.message})

    elif action == "set_name":
        if not request.POST["name"]:
            raise PermissionDenied("Name can't be blank")
        request.session["name"] = request.POST["name"]
        return JsonResponse({"success": 1})

    return JsonResponse({"message": f"No such method {action}"}, status=400)


# -- Staff views --


class PuzzleUpdate(UpdateView[Puzzle, BaseModelForm[Puzzle]], StaffRequiredMixin):
    model = Puzzle
    context_object_name = "puzzle"
    fields = (
        "name",
        "slug",
        "status_progress",
        "flavor_text",
        "content",
        "puzzle_head",
    )


class SolutionUpdate(
    UpdateView[Solution, BaseModelForm[Solution]],
    StaffRequiredMixin,
    GeneralizedSingleObjectMixin,
):
    model = Solution
    context_object_name = "solution"
    fields = (
        "post_solve_story",
        "solution_text",
        "author_notes",
        "post_solve_image_path",
        "post_solve_image_path",
    )


class RoundUpdate(
    UpdateView[Round, BaseModelForm[Round]],
    StaffRequiredMixin,
    GeneralizedSingleObjectMixin,
):
    model = Round
    context_object_name = "round"
    fields = (
        "name",
        "chapter_number",
        "show_chapter_number",
        "slug",
        "thumbnail_path",
        "round_text",
    )


class UnlockableUpdate(
    UpdateView[Unlockable, BaseModelForm[Unlockable]],
    StaffRequiredMixin,
    GeneralizedSingleObjectMixin,
):
    model = Unlockable
    context_object_name = "unlockable"
    fields = (
        "name",
        "slug",
        "story_only",
        "intro_story_text",
        "force_visibility",
        "courage_bounty",
    )


class StaffHuntList(ListView[Hunt], StaffRequiredMixin):
    """Staff view of all the hunts"""

    context_object_name = "hunt_list"
    model = Hunt
    template_name = "core/staff_hunt_list.html"

    def get_queryset(self):
        return Hunt.objects.order_by("-start_date")


class StaffPuzzleList(ListView[Puzzle], StaffRequiredMixin):
    """Staff list of the puzzles"""

    context_object_name = "puzzle_list"
    model = Puzzle
    template_name = "core/staff_puzzle_list.html"

    def get_queryset(self):
        return (
            Puzzle.objects.filter(status_progress__range=(0, 6))
            .order_by("status_progress")
            .select_related("unlockable", "solution")
        )


class StaffUnlockableList(ListView[Unlockable], StaffRequiredMixin):
    """Staff list of unlockables"""

    context_object_name = "unlockable_list"
    model = Unlockable
    template_name = "core/staff_unlockable_list.html"

    def get_queryset(self):
        self.hunt = Hunt.objects.get(**self.kwargs)
        return Unlockable.objects.filter(hunt=self.hunt).order_by("sort_order")

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        context["hunt"] = self.hunt
        return context
