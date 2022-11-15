from typing import Any, Dict

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse  # NOQA
from django.http.response import HttpResponseBase
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView

from .models import Attempt, Hunt, Puzzle, Round, SaltedAnswer, Solution, TestSolveSession, Unlockable, get_viewable  # NOQA
from .utils import get_token_from_request


class StaffRequiredMixin(PermissionRequiredMixin):
    permission_required = 'is_staff'


class GeneralizedSingleObjectMixin(SingleObjectMixin[Any]):

    def get_object(self, queryset: QuerySet[Any] = None):
        kwargs = self.kwargs  # type: ignore
        if queryset is None:
            queryset = self.get_queryset()
        for keyword in kwargs:
            if kwargs[keyword] == '-':
                kwargs.pop(keyword)
                kwargs[keyword + '__isnull'] = True
        return queryset.get(**kwargs)


Context = Dict[str, Any]


class HuntList(ListView[Hunt]):
    """Top-level list of all the hunts"""
    context_object_name = "hunt_list"
    model = Hunt

    def get_queryset(self):
        return Hunt.objects.filter(visible=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = get_token_from_request(self.request)
        return context


class RoundUnlockableList(ListView[Unlockable]):
    """List of all the top-level rounds in a given hunt"""
    context_object_name = "round_unlockable_list"
    template_name = "core/round_unlockable_list.html"
    model = Unlockable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = get_token_from_request(self.request)
        context['token'] = token
        context['hunt'] = self.hunt
        if token is not None:
            context['courage'] = token.get_courage(self.hunt)
        return context

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        self.hunt = Hunt.objects.get(volume_number=self.kwargs['volume_number'])
        token = get_token_from_request(self.request)
        context = {'token': token, 'hunt': self.hunt}
        if not self.hunt.has_started and (token is None or token.is_plebian):
            return render(request, "core/too_early.html", context)
        if token is None and self.hunt.active:
            return render(request, "core/needs_token.html", context)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Unlockable]:
        token = get_token_from_request(self.request)
        queryset = Unlockable.objects.filter(
            hunt=self.hunt, parent__isnull=True).select_related('round')
        if self.hunt.active is True:
            if token is None:
                raise PermissionDenied("Need token for an active hunt")
            return get_viewable(self.hunt, queryset, token)
        return queryset


class UnlockableList(ListView[Unlockable]):
    """List of all the unlockables in a given round"""
    context_object_name = "unlockable_list"
    model = Unlockable

    def dispatch(self, request: HttpRequest, *args: Any,
                 **kwargs: Any) -> HttpResponseBase:
        self.cheating = self.kwargs.pop('cheating', False)
        self.round = Round.objects.get(**self.kwargs)
        assert self.round.unlockable is not None
        self.hunt = self.round.unlockable.hunt
        token = get_token_from_request(request)

        if token is None:
            if self.hunt.has_ended:
                return super().dispatch(request, *args, **kwargs)
            else:
                raise PermissionDenied()
        elif not token.has_unlocked(self.round.unlockable):
            return HttpResponseRedirect(
                self.round.unlockable.get_absolute_url())
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Unlockable]:
        token = get_token_from_request(self.request)
        if token is None:
            if self.hunt.has_ended:
                return Unlockable.objects.filter(parent=self.round)
            else:
                raise PermissionDenied(
                    "Token None cannot participate in active hunt")
        else:
            assert self.round.unlockable is None or token.can_unlock(
                self.round.unlockable)
            queryset: QuerySet[Unlockable] = Unlockable.objects.filter(
                parent=self.round)
            if self.cheating is True and self.round.unlockable is not None:
                if not self.round.unlockable.hunt.can_cheat(token):
                    raise PermissionDenied("Cheating not allowed yet")
            else:
                queryset = get_viewable(self.hunt, queryset, token)
            queryset = queryset.annotate(round_exists=Count('round'))
            queryset = queryset.order_by(
                'sort_order',
                'name',
            )
            queryset = queryset.select_related('puzzle', 'round')
            return queryset

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        token = get_token_from_request(self.request)
        context['token'] = token
        context['round'] = self.round
        context['cheating'] = self.cheating
        if token is not None and self.round.unlockable is not None:
            context['courage'] = token.get_courage(self.round.unlockable.hunt)
        return context


class PuzzleDetail(DetailView[Puzzle]):
    """Shows a puzzle"""
    model = Puzzle
    context_object_name = "puzzle"
    object: Puzzle

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        token = get_token_from_request(self.request)
        context['token'] = token
        if token is not None and self.object.unlockable is not None:
            context['courage'] = token.get_courage(self.object.unlockable.hunt)
        return context

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        ret = super().dispatch(request, *args, **kwargs)
        token = get_token_from_request(self.request)
        if self.object.unlockable is None:
            if token is not None and not token.is_plebian:
                return ret
            else:
                raise PermissionDenied(
                    "Puzzle has no unlockable yet, not rendering")
        hunt = self.object.unlockable.hunt
        if not hunt.has_started:
            return render(request, "core/too_early.html", {'token': token})
        if not self.object.unlockable.hunt.has_ended:
            if token is not None:
                u = self.object.unlockable
                if u.hunt.active is True:
                    assert token.has_unlocked(u)
        return ret


class PuzzleDetailTestSolve(DetailView[Puzzle], GeneralizedSingleObjectMixin):
    """Shows a puzzle, no questions asked"""
    model = Puzzle
    context_object_name = "puzzle"
    object: Puzzle

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        token = get_token_from_request(self.request)
        context['token'] = token
        if token is not None and self.object.unlockable is not None:
            context['courage'] = token.get_courage(self.object.unlockable.hunt)
        return context

    def dispatch(self, request: HttpRequest, *args: Any,
                 **kwargs: Any) -> HttpResponseBase:
        ret = super().dispatch(request, *args, **kwargs)
        token = get_token_from_request(request)
        if token is None or token.is_plebian:
            raise PermissionDenied()
        session = TestSolveSession.objects.get(
            uuid=self.kwargs['testsolvesession__uuid'])
        assert session.expires > timezone.now()
        return ret


class PuzzleSolutionDetail(DetailView[Puzzle]):
    """Shows a solution"""
    model = Puzzle
    context_object_name = "puzzle"
    template_name = 'core/puzzlesolution_detail.html'
    object: Puzzle

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        token = get_token_from_request(self.request)
        context['token'] = token
        if token is not None and self.object.unlockable is not None:
            context['courage'] = token.get_courage(self.object.unlockable.hunt)
        return context

    def dispatch(self, request: HttpRequest, *args: Any,
                 **kwargs: Any) -> HttpResponseBase:
        ret = super().dispatch(request, *args, **kwargs)
        self.cheating = kwargs.pop('cheating', False)
        token = get_token_from_request(self.request)
        u = self.object.unlockable
        if u is None:
            if token is not None and not token.is_plebian:
                return ret
            else:
                raise PermissionDenied(
                    "Puzzle has no unlockable yet, not rendering solution")
        elif u.hunt.active is True:
            assert token is not None
            if self.cheating is True:
                attempt, _ = Attempt.objects.get_or_create(unlockable=u,
                                                           token=token)
                if attempt.status != 1:
                    attempt.status = 1
                    attempt.save()
            else:
                if not token.has_solved(u):
                    raise PermissionDenied(
                        "Can't view solution to unsolved puzzle")
            return ret
        else:
            return ret


class UnlockableDetail(DetailView[Unlockable]):
    model = Unlockable
    context_object_name = "unlockable"
    object: Unlockable

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        token = get_token_from_request(self.request)
        context['token'] = token
        if token is not None:
            context['courage'] = token.get_courage(self.object.hunt)
        u = self.object  # type: ignore
        if token is not None:
            can_unlock = token.can_unlock(u)
            attempt, _ = Attempt.objects.get_or_create(unlockable=u,
                                                       token=token)
            context['locked'] = not can_unlock
            context['new'] = attempt.status < 0 and can_unlock
            if can_unlock and u.story_only is True and attempt.status < 1:
                attempt.status = 1
                attempt.save()
            elif can_unlock and attempt.status < 0:
                attempt.status = 0
                attempt.save()
        elif u.hunt.has_ended:
            context['locked'] = False
            context['new'] = False
        else:
            raise PermissionDenied()
        return context


@csrf_exempt
def ajax(request: HttpRequest) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'error': "☕"}, status=418)

    token = get_token_from_request(request)
    action = request.POST.get('action')
    if action == 'guess':
        puzzle = Puzzle.objects.get(slug=request.POST.get('puzzle_slug'))
        guess = request.POST.get('guess') or ''
        salt = int(request.POST.get('salt') or 0)
        sa = SaltedAnswer.objects.get(puzzle=puzzle, salt=salt)
        if not sa.equals(guess):
            return JsonResponse({'correct': 0})
        elif sa.is_correct:
            if puzzle.unlockable is not None and token is not None:
                a, _ = Attempt.objects.get_or_create(
                    token=token, unlockable=puzzle.unlockable)
                if a.status != 1:
                    a.status = 1
                    a.solved_on = timezone.now()
                    a.save()

                Attempt.objects.filter(
                    token=token, unlockable=puzzle.unlockable).update(status=1)
            return JsonResponse({
                'correct': 1,
                'url': puzzle.get_solution_url(),
            })
        else:
            return JsonResponse({'correct': 0.5, 'message': sa.message})

    elif action == 'log':
        raise NotImplementedError('TODO log')

    elif action == 'set_name':
        name = request.POST['name']
        token = get_token_from_request(request)
        if token is not None:
            token.name = name
            token.save()
            return JsonResponse({'success': 1})
        else:
            return JsonResponse({'success': 0})

    return JsonResponse({'message': f'No such method {action}'}, status=400)


# -- Staff views --


class PuzzleUpdate(UpdateView[Puzzle, BaseModelForm[Puzzle]],
                   StaffRequiredMixin):
    model = Puzzle
    context_object_name = "puzzle"
    fields = (
        'name',
        'slug',
        'status_progress',
        'flavor_text',
        'content',
        'puzzle_head',
    )


class SolutionUpdate(UpdateView[Solution, BaseModelForm[Solution]],
                     StaffRequiredMixin, GeneralizedSingleObjectMixin):
    model = Solution
    context_object_name = "solution"
    fields = (
        'post_solve_story',
        'solution_text',
        'author_notes',
        'post_solve_image_path',
        'post_solve_image_path',
    )


class RoundUpdate(UpdateView[Round, BaseModelForm[Round]], StaffRequiredMixin,
                  GeneralizedSingleObjectMixin):
    model = Round
    context_object_name = "round"
    fields = ('name', 'chapter_number', 'show_chapter_number', 'slug',
              'thumbnail_path', 'round_text')


class UnlockableUpdate(UpdateView[Unlockable, BaseModelForm[Unlockable]],
                       StaffRequiredMixin, GeneralizedSingleObjectMixin):
    model = Unlockable
    context_object_name = "unlockable"
    fields = ('name', 'slug', 'story_only', 'intro_story_text',
              'force_visibility', 'courage_bounty')


class StaffHuntList(ListView[Hunt], StaffRequiredMixin):
    """Staff view of all the hunts"""
    context_object_name = "hunt_list"
    model = Hunt
    template_name = 'core/staff_hunt_list.html'

    def get_queryset(self):
        return Hunt.objects.order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = get_token_from_request(self.request)
        return context


class StaffPuzzleList(ListView[Puzzle], StaffRequiredMixin):
    """Staff list of the puzzles"""
    context_object_name = "puzzle_list"
    model = Puzzle
    template_name = 'core/staff_puzzle_list.html'

    def get_queryset(self):
        return Puzzle.objects.filter(status_progress__range=(
            0, 6)).order_by('status_progress').select_related(
                'unlockable', 'solution')


class StaffUnlockableList(ListView[Unlockable], StaffRequiredMixin):
    """Staff list of unlockables"""
    context_object_name = "unlockable_list"
    model = Unlockable
    template_name = 'core/staff_unlockable_list.html'

    def get_queryset(self):
        self.hunt = Hunt.objects.get(**self.kwargs)
        return Unlockable.objects.filter(hunt=self.hunt).order_by('sort_order')

    def get_context_data(self, **kwargs: Any) -> Context:
        context = super().get_context_data(**kwargs)
        context['hunt'] = self.hunt
        return context
