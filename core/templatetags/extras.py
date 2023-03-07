from typing import Any

import markdown
from django import template
from django.contrib.messages import constants as message_constants
from django.contrib.messages.storage.base import Message
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

import core.progresso
from core.models import Unlockable

register = template.Library()


def convert_to_markdown(s: str) -> str:
    return markdown.markdown(
        s,
        extensions=(
            "extra",
            "sane_lists",
            "smarty",
            "codehilite",
        ),
        extension_configs={
            "codehilite": {
                "linenums": False,
            }
        },
    )


MESSAGE_LEVEL_CLASSES = {
    message_constants.DEBUG: "border-indigo-600 bg-indigo-50 text-indigo-700",
    message_constants.INFO: "border-blue-600 bg-blue-50 text-blue-700",
    message_constants.SUCCESS: "border-green-600 bg-green-50 text-green-700",
    message_constants.WARNING: "border-yellow-600 bg-yellow-50 text-yellow-700",
    message_constants.ERROR: "border-red-600 bg-red-50 text-red-700 ",
}


@register.filter
def tailwind_message_classes(message: Message) -> str:
    """Return the message classes for a message."""
    extra_tags = None
    try:
        extra_tags = message.extra_tags
    except AttributeError:
        pass
    if extra_tags is None:
        extra_tags = ""
    else:
        extra_tags += " "
    try:
        level = message.level
    except AttributeError:
        pass
    else:
        try:
            extra_tags += MESSAGE_LEVEL_CLASSES[level]
        except KeyError:
            extra_tags += MESSAGE_LEVEL_CLASSES[message_constants.ERROR]
    return extra_tags


@register.filter(is_safe=True)
def mkd(value: str) -> str:
    return mark_safe(convert_to_markdown(value))


@register.filter(is_safe=True)
def emoji_link(href: str, emoji: str) -> str:
    return mark_safe(f'<a class="emoji-link" href="{href}">{emoji}</a>')


@register.filter()
def admin_url(obj: Any) -> str:
    return reverse(
        "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
        args=[obj.id],
    )


@register.filter()
def get_courage(request: HttpRequest):
    return core.progresso.get_courage(request)


@register.filter()
def get_name(request: HttpRequest):
    return core.progresso.get_name(request)


@register.filter()
def has_unlocked(request: HttpRequest, u: Unlockable):
    return core.progresso.check_unlocked(request, u)


@register.filter()
def has_solved(request: HttpRequest, u: Unlockable):
    return core.progresso.has_solved(request, u)


@register.filter()
def has_opened(request: HttpRequest, u: Unlockable):
    return core.progresso.has_opened(request, u)


@register.filter()
def get_tr_class(request: HttpRequest, u: Unlockable):
    if core.progresso.has_opened(request, u):
        if u.is_puzzle:
            if core.progresso.has_solved(request, u):
                s = "bg-blue-50"
            else:
                s = "Bg-yellow-100"
        elif u.story_only:
            s = "bg-gray-100"
        else:
            s = ""
    elif core.progresso.check_unlocked(request, u):
        s = "bg-green-200"
    elif u.story_only:
        s = "Bg-gray-200 opacity-50"
    else:
        s = "opacity-50"

    if (puzzle := getattr(u, "puzzle", None)) is not None and puzzle.is_meta:
        s += " font-bold"
    return s


@register.filter()
def get_finished_url(request: HttpRequest, u: Unlockable):
    return core.progresso.get_finished_url(request, u)
