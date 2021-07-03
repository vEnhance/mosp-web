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

@register.filter(is_safe=True)
def emoji_link(href : str, emoji : str) -> str:
	return mark_safe(f'<a class="emoji-link" href="{href}">{emoji}</a>')

@register.filter
def has_unlocked(token : models.Token, u : models.Unlockable) -> bool:
	return token.has_unlocked(u)
