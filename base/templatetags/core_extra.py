# coding:utf-8
from decimal import Decimal

from django import template
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.datetime_safe import datetime
from base.models import Termo

register = template.Library()


@register.simple_tag(takes_context=True)
def termos(context):
    return Termo.objects.filter(visivel=True)


@register.filter(name='currency')
def currency(numero):
    if numero:
        numero = float(numero)
    else:
        numero = 0
    return "R$ %s,%s" % (intcomma(int(numero)).replace(',', '.'), ("%0.2f" % numero)[-2:])


@register.filter(name='multiply')
def multiply(numero, arg):
    return float(numero) * float(arg)


@register.filter(name='add')
def add(numero, arg):
    return float(numero) + float(arg)


# settings value
@register.simple_tag
def settings_value(name):
    try:
        return settings.__getattr__(name)
    except AttributeError:
        return ""


@register.simple_tag(takes_context=True)
def have_group(context, user, name):
    context['user_%s' % name] = bool(user.groups.filter(name=name).exists())
    return ''


@register.filter
def str_to_cpf(value):
    if value:
        return u'%s.%s.%s-%s' % (value[:3], value[3:6], value[6:9], value[9:])
    else:
        return ''


@register.filter(name='strptime')
def strptime(value, mash):
    return datetime.strptime(value, mash)
