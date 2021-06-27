from django import template
from django.utils.safestring import mark_safe
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
def mkd(value):
	return mark_safe(convert_to_markdown(value))
