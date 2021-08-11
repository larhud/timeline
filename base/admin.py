from django.contrib import admin, messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from poweradmin.admin import PowerModelAdmin, InlineModelAdmin, PowerButton
from .forms import LinhaFormSet, InlineChangeList

from .models import Noticia, Termo, Assunto
from poweradmin.admin import PowerModelAdmin, InlineModelAdmin, PowerButton
from .forms import LinhaFormSet, InlineChangeList


class AssuntoAdmin(PowerModelAdmin):
    pass


class NoticiaAdmin(PowerModelAdmin):
    pass


class TermoAdmin(PowerModelAdmin):
    search_fields = ('termo',)
    list_display = ('termo', 'num_reads', 'id_externo')


admin.site.register(Termo, TermoAdmin)
admin.site.register(Noticia, NoticiaAdmin)
admin.site.register(Assunto, AssuntoAdmin)




