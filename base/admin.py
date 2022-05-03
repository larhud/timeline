import hashlib

from django.contrib import admin, messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from django import forms

from .models import Noticia, Termo, Assunto
from django.forms.widgets import NumberInput, URLInput
from poweradmin.admin import PowerModelAdmin, InlineModelAdmin, PowerButton


class AssuntoInline(InlineModelAdmin):
    model = Assunto


class NoticiaFormAdd(forms.ModelForm):
    termo = forms.ModelChoiceField(label='Termo', queryset=Termo.objects.all(), required=True)
    url = forms.URLField(widget=URLInput(attrs={'width': '120'}))
    dt = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    id_externo = forms.IntegerField(label='Identificador', required=False)

    class Meta:
        model = Noticia
        fields = ['termo', 'url', 'dt', 'id_externo']

    def clean(self):
        super().clean()
        id = self.cleaned_data['id_externo']
        url_hash = hashlib.sha256( self.cleaned_data['url'].encode('utf-8')).hexdigest()
        if Noticia.objects.filter(id_externo=id, assunto__termo__id=self.cleaned_data['termo'].id).count() > 0:
            raise forms.ValidationError('Já existe uma notícia com esse identificador')
        if Noticia.objects.filter(url_hash=url_hash):
            raise forms.ValidationError('Essa URL já foi registrada')


class NoticiaAdmin(PowerModelAdmin):
    multi_search = (
        ('q1', 'Texto', ['titulo', 'texto']),
        ('q2', 'URL', ['url']),
        ('q3', 'ID', ['id_externo']),
    )
    list_filter = ('url_valida', 'atualizado', 'revisado', 'visivel', 'assunto__termo')
    date_hierarchy = 'dt'
    list_display = ('id_externo', 'dt', 'titulo', 'fonte', 'url_valida', 'revisado')
    ordering = ('id_externo',)
    fields = (('dt', 'id_externo'), 'titulo', 'url', 'texto',
              ('fonte', 'url_valida', 'atualizado', 'revisado', 'visivel'),
              'media', 'texto_completo', 'nuvem', 'texto_busca', 'imagem')

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                        (None, {
                            'fields': ('termo', 'url', 'dt', 'id_externo')
                        }),
                    )
        return super(NoticiaAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.form = NoticiaFormAdd
            kwargs['fields'] = ['url',]
        return super(NoticiaAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'texto_completo':
            kwargs['widget'] = forms.Textarea(attrs={'rows': 15, 'cols': 110})
        if db_field.name in ['texto','titulo']:
            kwargs['widget'] = forms.Textarea(attrs={'rows': 2, 'cols': 110})
        return super(NoticiaAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_buttons(self, request, object_id):
        buttons = super(NoticiaAdmin, self).get_buttons(request, object_id)
        if object_id:
            buttons.append(
                PowerButton(url=reverse('get_pdf', kwargs={'id': object_id, }),
                            label=u'Visualiza PDF'))
            buttons.append(
                PowerButton(url=reverse('scrap_text', kwargs={'id': object_id, }),
                            label=u'Capturar Texto'))
        return buttons

    def get_actions(self, request):
        actions = super(NoticiaAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def marca_visibilidade(self, request, queryset):
        total = queryset.update(visivel=False, texto_busca=None, nuvem=None)
        self.message_user(request, u'Notícias invisibilizadas: %d' % total)
    marca_visibilidade.short_description = u'Invisibiliza Notícias'

    actions = [marca_visibilidade, ]

    def save_model(self, request, obj, form, change):
        if change:
            super(NoticiaAdmin, self).save_model(request, obj, form, change)
        else:
            id_externo = form.cleaned_data['id_externo']
            termo = form.cleaned_data['termo']
            if not id_externo:
                ultima_noticia = Assunto.objects.filter(termo=termo.id).order_by('id_externo').last()
                id_externo = ultima_noticia.id_externo + 1
            obj.dt = form.cleaned_data['dt']
            obj.url = form.cleaned_data['url']
            obj.id_externo = id_externo
            obj.save()
            Assunto.objects.create(noticia=obj, termo=termo, id_externo=id_externo)


class TermoAdmin(PowerModelAdmin):
    search_fields = ('termo',)
    list_display = ('termo', 'slug', 'tot_noticias',)
    readonly_fields = ('tot_noticias',)


admin.site.register(Termo, TermoAdmin)
admin.site.register(Noticia, NoticiaAdmin)



