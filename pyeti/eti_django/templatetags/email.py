from urllib.parse import quote

from django import template
from django.forms.utils import flatatt
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape, escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()


def _obfuscate(string):
    """
    Given a string, return that string obfuscated for display on a web page.
    """
    return ''.join(['&#%s;' % ord(char) for char in string])


_MAILTO = _obfuscate('ma') + 'ilto:'


@register.filter
@stringfilter
@mark_safe
def obfuscate(value):
    return _obfuscate(conditional_escape(value))


@register.filter
@stringfilter
def obfuscate_mailto(value, text=None, **attrs):
    mail = obfuscate(value)
    url = '%s%s' % (_MAILTO, mail)

    if text and ';' in text:
        text, subject = text.split(';')
        url += '?subject=' + quote(escape(subject))

    if not text:
        text = mail

    attrs.update({
        'href': mark_safe(url),  # noqa: S308, S703
    })
    return format_html('<a{}>{}</a>', flatatt(attrs), text)
