# coding: utf-8
from django import template
from powercms.cms.models import Menu
from urllib.parse import urlparse


register = template.Library()


@register.inclusion_tag('includes/menu.html', takes_context=True)
def show_menu(context):
    menu_itens_pk = []
    for menu in Menu.objects.filter(is_active=True):
        if menu.have_perm(context.get('request').user):
            menu_itens_pk.append(menu.pk)
    return {
        'request': context.get('request', None),
        'menu_itens': Menu.objects.filter(pk__in=menu_itens_pk).order_by('tree_id'),
    }


@register.filter
def is_active(menu, request):
    menu_url = menu.get_link()
    if menu_url:
        parsed_menu_url = urlparse(menu_url)
        return parsed_menu_url.path == request.path

    return False
