from django import template
from django.utils.safestring import mark_safe
from .. import models
from typing import Optional
import markdown

register = template.Library()

def convert_to_markdown(s : str) -> str:
	return markdown.markdown(s,
			extensions = (
				'extra',
				'sane_lists',
				'smarty',
				'codehilite',
				),
			extension_configs = {
				'codehilite' : {
					'linenums' : False,
					}
				}
			)

@register.filter(is_safe=True)
def mkd(value) -> str:
	return mark_safe(convert_to_markdown(value))

@register.filter
def emoji_link(href : str, emoji : str) -> str:
	return f'<a class="emoji-link" href="{href}">{emoji}</a>'

@register.filter
def has_unlocked(token : models.Token, u : models.Unlockable) -> bool:
	return token.has_unlocked(u)

@register.filter
def firstname(token : Optional[models.Token]) -> str:
	if token is not None:
		return f'<span class="name firstname">{token.firstname}</span>'
	else:
		return f'<span class="name firstname"></span>'

@register.filter
def fullname(token : models.Token) -> str:
	if token is not None:
		return f'<span class="name fullname">{token.name}</span>'
	else:
		return f'<span class="name fullname"></span>'
