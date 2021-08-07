from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from .. import models
import markdown

register = template.Library()

def convert_to_markdown(s: str) -> str:
	return markdown.markdown(s,
			extensions = (
				'extra',
				'sane_lists',
				'smarty',
				'codehilite',
				),
			extension_configs = {
				'codehilite': {
					'linenums': False,
					}
				}
			)

from django.contrib.messages import constants as message_constants
MESSAGE_LEVEL_CLASSES = {
    message_constants.DEBUG: "border-indigo-600 bg-indigo-50 text-indigo-700",
    message_constants.INFO: "border-blue-600 bg-blue-50 text-blue-700",
    message_constants.SUCCESS: "border-green-600 bg-green-50 text-green-700",
    message_constants.WARNING: "border-yellow-600 bg-yellow-50 text-yellow-700",
    message_constants.ERROR: "border-red-600 bg-red-50 text-red-700 ",
}

@register.filter
def tailwind_message_classes(message):
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
def mkd(value) -> str:
	return mark_safe(convert_to_markdown(value))

@register.filter(is_safe=True)
def emoji_link(href: str, emoji: str) -> str:
	return mark_safe(f'<a class="emoji-link" href="{href}">{emoji}</a>')

@register.filter()
def admin_url(obj) -> str:
	 return reverse('admin:%s_%s_change' % (obj._meta.app_label,  obj._meta.model_name),  args=[obj.id] )

@register.filter
def has_found(token: models.Token, u: models.Unlockable) -> bool:
	return token.has_found(u)
@register.filter
def has_unlocked(token: models.Token, u: models.Unlockable) -> bool:
	return token.has_unlocked(u)
@register.filter
def has_solved(token: models.Token, u: models.Unlockable) -> bool:
	return token.has_solved(u)
@register.filter
def can_unlock(token: models.Token, u: models.Unlockable) -> bool:
	return token.can_unlock(u)
@register.filter
def can_cheat(token: models.Token, hunt: models.Hunt) -> bool:
	return hunt.allow_cheat(token)
@register.filter
def get_finished_url(token: models.Token, u: models.Unlockable) -> str:
	return u.get_finished_url(token)
