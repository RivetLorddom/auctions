from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def shorten(value):
    if len(value) > 41:
        return value[0:40]+ "..."
    return value