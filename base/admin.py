import hashlib

from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms.widgets import ClearableFileInput
from django.forms.widgets import NumberInput, URLInput
from django.urls import reverse
from poweradmin.admin import PowerModelAdmin, InlineModelAdmin, PowerButton

from .models import Noticia, Termo, Assunto


class AssuntoInline(InlineModelAdmin):
    model = Assunto


class NoticiaFormAdd(forms.ModelForm):
    termo = forms.ModelChoiceField(label='Termo', queryset=Termo.objects.all(), required=True, initial=Termo.objects.last().id)
    url = forms.URLField(widget=URLInput(attrs={'size': 100}), required=True)
    dt = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    fonte = forms.CharField(label='Fonte da Notícia', widget=URLInput(attrs={'size': 60}), required=True)
    id_externo = forms.IntegerField(label='Identificador', required=False)

    class Meta:
        model = Noticia
        fields = ['termo', 'url', 'dt', 'fonte', 'id_externo']

    def clean(self):
        cleaned_data = super(NoticiaFormAdd, self).clean()
        if self.cleaned_data.get('url'):
            url_hash = hashlib.sha256(self.cleaned_data['url'].encode('utf-8')).hexdigest()
            if Noticia.objects.filter(url_hash=url_hash):
                raise forms.ValidationError('Essa URL já foi registrada')
            id = self.cleaned_data['id_externo']
            if id:
                if Noticia.objects.filter(id_externo=id, assunto__termo__id=self.cleaned_data['termo'].id).count() > 0:
                    raise forms.ValidationError('Já existe uma notícia com esse identificador')
        return cleaned_data


class NoticiaEdit(forms.ModelForm):
    extra_field = forms.FileField(label='Espelho em PDF', required=False,
                                  widget=ClearableFileInput(attrs={'accept': '.pdf'}))

    def save(self, commit=True):
        extra_field = self.cleaned_data.get('extra_field', None)

        instance = super(NoticiaEdit, self).save(commit=commit)

        if extra_field:
            with open(f'{settings.MEDIA_ROOT}/pdf/{instance.id}.pdf', 'wb+') as destination:
                for chunk in extra_field.chunks():
                    destination.write(chunk)

            instance.pdf_atualizado = True
            instance.save()

        return instance

    class Meta:
        model = Noticia
        fields = "__all__"


class NoticiaAdmin(PowerModelAdmin):
    multi_search = (
        ('q1', 'Texto', ['titulo', 'texto']),
        ('q2', 'URL', ['url']),
        ('q3', 'ID', ['id_externo']),
        ('q4', 'Veículo', ['fonte']),
    )
    list_filter = ('url_valida', 'atualizado', 'revisado', 'visivel', 'assunto__termo')
    date_hierarchy = 'dt'
    list_display = ('id_externo', 'dt', 'titulo', 'fonte', 'url_valida', 'revisado', 'visivel')
    ordering = ('id_externo',)
    fields = (('dt', 'id_externo'), 'titulo', 'url', 'texto',
              ('fonte', 'url_valida', 'atualizado', 'revisado', 'coletanea', 'visivel'),
              'media', 'texto_completo', 'nuvem', 'texto_busca', 'imagem_link', 'extra_field', 'pdf_file', 'notas')
    readonly_fields = ('pdf_file', 'imagem_link')

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (None, {
                    'fields': ('termo', 'url', 'dt', 'fonte', 'id_externo')
                }),
            )
        return super(NoticiaAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.form = NoticiaFormAdd
            kwargs['fields'] = ['url', ]
        else:
            self.form = NoticiaEdit
        return super(NoticiaAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'texto_completo':
            kwargs['widget'] = forms.Textarea(attrs={'rows': 15, 'cols': 120})
        elif db_field.name in ['texto', 'titulo']:
            kwargs['widget'] = forms.Textarea(attrs={'rows': 3, 'cols': 120})
        elif db_field.name in ['nuvem', 'texto_busca']:
            kwargs['widget'] = forms.Textarea(attrs={'rows': 2, 'cols': 150})
        # if db_field.name == 'pdf_file':
        #    kwargs['widget'] = PDFInput()
        return super().formfield_for_dbfield(db_field, **kwargs)

    def get_buttons(self, request, object_id):
        buttons = super(NoticiaAdmin, self).get_buttons(request, object_id)
        if object_id:
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
            # super().save_model(request, obj, form, change)
            obj.save(form=form)
        else:
            id_externo = form.cleaned_data['id_externo']
            termo = form.cleaned_data['termo']
            if not id_externo:
                ultima_noticia = Assunto.objects.filter(termo=termo.id).order_by('id_externo').last()
                if not ultima_noticia:
                    id_externo = 1
                else:
                    id_externo = ultima_noticia.id_externo + 1
            obj.dt = form.cleaned_data['dt']
            obj.url = form.cleaned_data['url']
            obj.fonte = form.cleaned_data['fonte']
            obj.id_externo = id_externo
            obj.save()
            Assunto.objects.create(noticia=obj, termo=termo, id_externo=id_externo)


class TermoAdmin(PowerModelAdmin):
    search_fields = ('termo',)
    list_display = ('termo', 'slug', 'tot_noticias',)
    readonly_fields = ('tot_noticias',)


admin.site.register(Termo, TermoAdmin)
admin.site.register(Noticia, NoticiaAdmin)
