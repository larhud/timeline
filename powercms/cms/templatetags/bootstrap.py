# coding:utf-8
from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter(name='btform')
def btform(field):
    html = u'%s' % field
    if (not 'type="radio"' in html) and (not 'type="checkbox"' in html):
        html = html.replace('name=', 'class="form-control" name=')
    return mark_safe(html)

@register.filter(name='btischeckbox')
def btischeckbox(field):
    if 'type="checkbox"' in str(field):
        return True
    return False