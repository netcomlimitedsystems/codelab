# courses/templatetags/markdown_extras.py
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(
        text,
        extensions=[
            'fenced_code',
            'tables', 
            'nl2br',
            'codehilite',  # For syntax highlighting
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
            }
        }
    ))