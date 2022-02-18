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


class AssuntoInline(InlineModelAdmin):
    model = Assunto


class NoticiaAdmin(PowerModelAdmin):
    search_fields = ('titulo',)
    date_hierarchy = 'dt'
    list_display = ('dt', 'titulo', )
    # inlines = (AssuntoInline,)


class TermoAdmin(PowerModelAdmin):
    search_fields = ('termo',)
    list_display = ('termo', 'tot_noticias',  'id_externo')
    readonly_fields = ('tot_noticias',)


admin.site.register(Termo, TermoAdmin)
admin.site.register(Noticia, NoticiaAdmin)



