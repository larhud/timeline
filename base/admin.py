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
    search_fields = ('titulo', 'texto', 'url')
    list_filter = ('url_valida', 'atualizado', 'revisado')
    date_hierarchy = 'dt'
    list_display = ('id_externo', 'dt', 'titulo', 'fonte', 'url_valida', 'revisado')
    ordering = ('id_externo',)
    fields = ('id_externo', 'dt', 'titulo', 'url', 'texto', ('fonte', 'url_valida', 'atualizado', 'revisado',),
              'media', 'texto_completo', 'nuvem', 'texto_busca', 'imagem')
    # inlines = (AssuntoInline,)

    def get_buttons(self, request, object_id):
        buttons = super(NoticiaAdmin, self).get_buttons(request, object_id)
        if object_id:
            buttons.append(
                PowerButton(url=reverse('get_pdf', kwargs={'id': object_id, }),
                            label=u'Visualiza PDF'))
        return buttons


class TermoAdmin(PowerModelAdmin):
    search_fields = ('termo',)
    list_display = ('termo', 'tot_noticias',  'id_externo')
    readonly_fields = ('tot_noticias',)


admin.site.register(Termo, TermoAdmin)
admin.site.register(Noticia, NoticiaAdmin)



