import re

from django import template

try:
    from django.urls import reverse, NoReverseMatch
except ImportError:
    from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname, is_pattern=True):
    path = context['request'].path
    try:
        reversed = reverse(pattern_or_urlname)
    except NoReverseMatch:
        reversed = pattern_or_urlname
    if is_pattern:
        if re.search("^" + reversed, path):
            return 'round-current'
    else:
        if reversed == path:
            return 'round-current'
    return ''
