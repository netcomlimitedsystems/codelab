# courses/templatetags/markdown_extras.py
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    if not text:
        return ""
    
    # Create markdown processor with extensions
    md = markdown.Markdown(
        extensions=[
            'fenced_code',      # For code blocks with ```
            'codehilite',       # For syntax highlighting
            'tables',           # For tables
            'nl2br',            # Convert newlines to <br>
            'toc',              # Table of contents
            'sane_lists',       # Better list handling
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
                'guess_lang': True,
                'use_pygments': True,
            }
        }
    )
    
    return mark_safe(md.convert(text))