from django.db.models.aggregates import Sum
from django.http import HttpRequest
from django.utils import timezone

from .models import Unlockable
from .utils import is_staff


def mark_solved(request: HttpRequest, u: Unlockable):
    if not type(request.session.get("solved", None)) == list:
        request.session["solved"] = []
    if u.pk not in request.session["solved"]:
        request.session["solved"] += [u.pk]


def get_solved_pks(request: HttpRequest) -> list[int]:
    if not type(request.session.get("solved", None)) == list:
        request.session["solved"] = []
    return request.session["solved"]


def has_solved(request: HttpRequest, u: Unlockable) -> bool:
    return u.pk in get_solved_pks(request)


def mark_opened(request: HttpRequest, u: Unlockable):
    if not type(request.session.get("opened", None)) == list:
        request.session["opened"] = []
    if u.pk not in request.session["opened"]:
        request.session["opened"] += [u.pk]


def get_opened_pks(request: HttpRequest) -> list[int]:
    if not type(request.session.get("opened", None)) == list:
        request.session["opened"] = []
    return request.session["opened"]


def has_opened(request: HttpRequest, u: Unlockable) -> bool:
    return u.pk in get_opened_pks(request)


def set_courage(request: HttpRequest):
    request.session["courage"] = (
        Unlockable.objects.filter(
            hunt__start_date__lt=timezone.now(),
            hunt__end_date__gt=timezone.now(),
            pk__in=get_solved_pks(request),
        ).aggregate(courage=Sum("courage_bounty"))["courage"]
        or 0
    )


def get_courage(request: HttpRequest) -> int:
    if not type(request.session.get("courage", None)) == int:
        set_courage(request)
    return request.session["courage"] or 0


def check_unlocked(request: HttpRequest, u: Unlockable) -> bool:
    if not u.hunt.visible and not is_staff(request.user):
        return False
    elif u.hunt.has_ended:
        return True
    elif not u.hunt.has_started and not is_staff(request.user):
        return False
    elif u.force_visibility is True:
        return True

    courage = get_courage(request)
    solved_pks = get_solved_pks(request)

    if courage < u.unlock_courage_threshold:
        return False
    if u.unlock_date is not None and timezone.now() < u.unlock_date:
        return False
    if (needed := u.unlock_needs) is not None and not needed.pk in solved_pks:
        return False

    return True


def get_finished_url(request: HttpRequest, u: Unlockable) -> str:
    if u.on_solve_link_to is None:
        if u.parent is None:
            return u.hunt.get_absolute_url()
        else:
            return u.parent.get_absolute_url()
    elif u.on_solve_link_to.unlockable is None:
        return u.hunt.get_absolute_url()  # wtf
    elif has_opened(request, u.on_solve_link_to.unlockable):
        return u.on_solve_link_to.unlockable.get_absolute_url()
    else:
        return u.on_solve_link_to.get_absolute_url()


def get_name(request: HttpRequest) -> str:
    if not "name" in request.session:
        request.session["name"] = "Frisk"
    return request.session["name"]
