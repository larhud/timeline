# coding:utf-8
import io
import os
import zipfile
from datetime import datetime
from functools import partial
from threading import Thread

import requests
from bs4 import BeautifulSoup
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_mptt_admin.admin import DjangoMpttAdmin

from poweradmin.admin import PowerModelAdmin, PowerButton
from powercms.serialize import CustomSerializer
from .forms import ThemeForm, CustomGroupForm, PowerArticleForm
from .models import Menu, Section, Article, SectionItem, URLMigrate, \
    FileDownload, ArticleArchive, ArticleComment, EmailAgendado, Recurso, \
    Theme, Permissao, GroupType, GroupItem, ArticleAttribute, URLNotFound


class FileDownloadAdmin(PowerModelAdmin):
    list_display = ['title', 'file', 'count', 'expires_at']
    readonly_fields = ['count', 'download_url', ]
    fieldsets = (
        (None, {
            'fields': ['title', 'file', 'expires_at', 'create_article', 'count', 'download_url', ]
        }),
    )

    def get_buttons(self, request, object_id):
        buttons = super(FileDownloadAdmin, self).get_buttons(request, object_id)
        if object_id:
            obj = self.get_object(request, object_id)
            if obj.article:
                buttons.append(PowerButton(url=obj.article_url(), label='Artigo'))
        return buttons

    def save_model(self, request, obj, form, change):
        super(FileDownloadAdmin, self).save_model(request, obj, form, change)
        if obj.create_article and not obj.article:
            article = Article(
                title='Download %s' % obj.title,
                content='<a href="%s">Download</a>' % obj.get_absolute_url(),
                author=request.user,
            )
            article.save()
            obj.article = article
            obj.save()


admin.site.register(FileDownload, FileDownloadAdmin)


class URLMigrateAdmin(PowerModelAdmin):
    list_display = ['old_url', 'new_url', 'redirect_type', 'dtupdate', 'views']

    class Media:
        js = ('js/custom_admin.js',)


admin.site.register(URLMigrate, URLMigrateAdmin)


class SectionItemCreateInline(admin.TabularInline):
    model = SectionItem
    extra = 1

    def get_queryset(self, request):
        return super(SectionItemCreateInline, self).get_queryset(request).none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'article':
            kwargs['queryset'] = Article.objects.filter(is_active=True)
            return db_field.formfield(**kwargs)
        return super(SectionItemCreateInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SectionItemActiveInline(admin.TabularInline):
    model = SectionItem
    extra = 0
    readonly_fields = ['display_article_link', 'section', 'display_article_created_at']
    fields = ['display_article_link', 'section', 'order', 'display_article_created_at']

    def has_add_permission(self, request, obj=None):
        return False


class PermissaoSectionInline(admin.TabularInline):
    model = Permissao
    extra = 1


class SectionAdmin(PowerModelAdmin):
    list_display = ['title', 'views', 'conversions', 'num_articles', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order',)
    multi_search = (
        ('q1', 'Título', ['title']),
        ('q2', 'Slug', ['slug']),
    )
    fieldsets_superuser = (
        (None, {
            'fields': ['title', 'slug', 'header', 'keywords', 'order', 'template', ]
        }),
    )
    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'header', 'keywords', 'order']
        }),
    )
    inlines = [SectionItemActiveInline, SectionItemCreateInline, PermissaoSectionInline]

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return self.fieldsets_superuser
        return self.fieldsets

    def get_form(self, request, obj=None, **kwargs):
        defaults = {
            "form": self.form if not obj else forms.ModelForm,
            "fields": flatten_fieldsets(self.get_fieldsets(request, obj)),
            "exclude": self.get_readonly_fields(request, obj),
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        # defaults.update(kwargs)
        return modelform_factory(self.model, **defaults)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['header']:
            kwargs['widget'] = CKEditorUploadingWidget()

        return super(SectionAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Section, SectionAdmin)


class GroupItemGroupTypeInline(admin.TabularInline):
    model = GroupItem
    extra = 1


class GroupTypeAdmin(PowerModelAdmin):
    list_display = ['name', 'order']
    search_fields = ('name',)
    list_editable = ('order',)
    fieldsets = (
        (None, {
            'fields': ['name', 'order', ]
        }),
    )
    inlines = [GroupItemGroupTypeInline, ]


admin.site.register(GroupType, GroupTypeAdmin)


class SectionItemInline(admin.TabularInline):
    model = SectionItem
    extra = 0
    verbose_name_plural = 'Seções'


class ArticleAttributeInline(admin.TabularInline):
    model = ArticleAttribute
    extra = 1


class ArticleCommentInline(admin.TabularInline):
    model = ArticleComment
    extra = 0
    fields = ('created_at', 'author', 'comment', 'active')
    readonly_fields = ('created_at', 'author', 'comment')


class ArticleAdmin(PowerModelAdmin):
    list_display = (
        'title', 'slug', 'get_sections_display', 'created_at', 'is_active', 'allow_comments', 'views', 'conversions',
        'likes',)
    list_editable = ('is_active',)
    list_filter = ('created_at',)
    multi_search = (
        ('q1', 'Título', ['title']),
        ('q2', 'Conteúdo', ['content']),
        ('q3', 'Palavras Chaves', ['keywords']),
        ('q4', 'Seção', ['sectionitem__section__title']),
    )
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {'fields': [('title', 'slug'), 'header', 'content', 'keywords', 'created_at', 'author', 'is_active',
                           'allow_comments', ]}),
        ('Meta tags', {'fields': ['og_title', 'og_image', ]}),
    )
    actions = ('reset_views', 'export_article',)
    raw_id_fields = ('author',)
    inlines = (SectionItemInline, ArticleAttributeInline, ArticleCommentInline,)

    @transaction.atomic
    def add_view(self, request, form_url='', extra_context=None):
        if request.user.has_perm('cms.manage_articles') and not (
                request.user.is_superuser or request.user.groups.filter(name='Editor').exists()):
            return HttpResponseRedirect(reverse('admin:cms_article_add_power'))
        return super(ArticleAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.has_perm('cms.manage_articles') and not (
                request.user.is_superuser or request.user.groups.filter(name='Editor').exists()):
            return HttpResponseRedirect(reverse('admin:cms_article_change_power', args=(object_id,)))
        return super(ArticleAdmin, self).change_view(request, object_id, form_url, extra_context)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['header', 'content']:
            kwargs['widget'] = CKEditorUploadingWidget()
        return super(ArticleAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['initial'] = request.user.id
            kwargs['queryset'] = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
        return super(ArticleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def clone(self, request, id):
        article_clone = Article.objects.get(pk=id)
        article_clone.pk = None
        article_clone.slug = None
        article_clone.views = 0
        article_clone.conversions = 0
        article_clone.created_at = datetime.now()
        article_clone.save()

        self.log_addition(request, article_clone, 'Adicionado.')

        for si in SectionItem.objects.filter(article__pk=id):
            si_clone = SectionItem(
                section=si.section,
                article=article_clone,
                order=si.order
            )
            si_clone.save()
        return HttpResponseRedirect(reverse('admin:cms_article_change', args=(article_clone.id,)))

    def add_power_view(self, request, form_url='', extra_context=None,
                       template_name='admin/cms/article/powerpost.html'):
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = PowerArticleForm
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                new_object.author = request.user

                if request.FILES.get('upload'):
                    # Salvar imagem, usando a view do ckeditor
                    from ckeditor.views import upload

                    url = upload(request).content
                    new_object.header = '<img src="%s" style="width: 50px; height: 37px;"/>%s' % (
                        url, new_object.header,)
                    new_object.content = '<img src="%s" style="width: 270px; height: 152px; margin: 10px; float: left;"/>%s' % (
                        url, new_object.content,)

                # Se for link colocar o slug == pk, e captura o titulo, chamada e imagem do artigo
                if form.cleaned_data.get('link'):
                    # try:
                    html = requests.get(form.cleaned_data.get('content')).text
                    soup = BeautifulSoup(html)
                    new_object.title = '%s' % soup.title.string
                    new_object.header = ''
                    if soup.select('meta[property="og:image"]'):
                        new_object.header += '<img style="width: 270px; height: 152px; margin: 10px; float: left;" src="%s">' % \
                                             soup.select('meta[property="og:image"]')[0].get('content')
                    if soup.select('meta[name="description"]'):
                        new_object.header += '%s' % soup.select('meta[name="description"]')[0].get('content')
                    # except: pass
                    new_object.save()
                    new_object.slug = new_object.pk

                new_object.save()

                if form.cleaned_data.get('section'):
                    new_object.sections.clear()
                    SectionItem(
                        section=form.cleaned_data.get('section'),
                        article=new_object
                    ).save()

                self.log_addition(request, new_object, 'Adicionado')
                messages.info(request, 'O artigo foi gravado com sucesso.')
                return HttpResponseRedirect(reverse('admin:cms_article_change_power', args=(new_object.pk,)))
        else:
            form = ModelForm()

        fieldsets = (
            (None, {
                'fields': ['link', ('title', 'slug'), 'header', 'content', 'is_active', 'upload', 'section', ]
            }),
        )
        adminForm = helpers.AdminForm(form, list(fieldsets), {'slug': ('title',)}, [], model_admin=self)
        media = self.media + adminForm.media

        context = {
            'add': True,
            'change': False,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, None),
            'has_delete_permission': self.has_delete_permission(request, None),
            'has_view_permission': self.has_view_permission(request, None),
            'has_file_field': True,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'title': 'Adicionar Artigo',
            'form_url': mark_safe(form_url),
            'opts': opts,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'adminform': adminForm,
            'is_popup': "_popup" in request.GET or "_popup" in request.POST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': [],
            'has_editable_inline_admin_formsets': False,
            'errors': helpers.AdminErrorList(form, []),
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, template_name, context)

    def change_power_view(self, request, object_id, form_url='', extra_context=None,
                          template_name='admin/cms/article/powerpost.html'):
        model = self.model
        opts = model._meta

        obj = self.get_object(request, unquote(object_id))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        ModelForm = PowerArticleForm
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            if form.is_valid():
                new_object = self.save_form(request, form, change=True)

                if request.FILES.get('upload'):
                    # Salvar imagem, usando a view do ckeditor
                    from ckeditor.views import upload

                    url = upload(request).content
                    new_object.header = '<img src="%s" style="width: 50px; height: 37px;"/>%s' % (
                        url, new_object.header,)
                    new_object.content = '<img src="%s" style="width: 270px; height: 152px; margin: 10px; float: left;"/>%s' % (
                        url, new_object.content,)

                # Se for link colocar o slug == pk, e captura o titulo, chamada e imagem do artigo
                if form.cleaned_data.get('link') == True:
                    # try:
                    html = requests.get(form.cleaned_data.get('content')).text
                    soup = BeautifulSoup(html)
                    new_object.title = '%s' % soup.title.string
                    new_object.header = ''
                    if soup.select('meta[property="og:image"]'):
                        new_object.header += '<img style="width: 270px; height: 152px; margin: 10px; float: left;" src="%s">' % \
                                             soup.select('meta[property="og:image"]')[0].get('content')
                    if soup.select('meta[name="description"]'):
                        new_object.header += '%s' % soup.select('meta[name="description"]')[0].get('content')
                    # except: pass
                    new_object.slug = new_object.pk

                new_object.save()

                if form.cleaned_data.get('section'):
                    new_object.sections.clear()
                    SectionItem(
                        section=form.cleaned_data.get('section'),
                        article=new_object
                    ).save()

                change_message = self.construct_change_message(request, form, [])
                self.log_change(request, new_object, change_message)
                messages.info(request, 'O artigo foi salvo com sucesso.')
                return HttpResponseRedirect(reverse('admin:cms_article_change_power', args=(new_object.pk,)))
        else:
            form = ModelForm(instance=obj)

        fieldsets = (
            (None, {
                'fields': ['link', ('title', 'slug'), 'header', 'content', 'is_active', 'upload', 'section', ]
            }),
        )
        adminForm = helpers.AdminForm(form, list(fieldsets), {'slug': ('title',)}, [], model_admin=self)
        media = self.media + adminForm.media

        context = {
            'add': False,
            'change': True,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, None),
            'has_delete_permission': self.has_delete_permission(request, None),
            'has_file_field': True,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'title': 'Editar %s' % obj,
            'object_id': object_id,
            'content_type_id': ContentType.objects.get_for_model(obj).pk,
            'original': obj,
            'ordered_objects': opts.get_ordered_objects(),
            'form_url': mark_safe(form_url),
            'opts': opts,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': [],
            'errors': helpers.AdminErrorList(form, []),
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, template_name, context, current_app=self.admin_site.name)

    def get_urls(self):
        urls = super(ArticleAdmin, self).get_urls()
        return [
            url(r'^add-power/$', self.wrap(self.add_power_view), name='cms_article_add_power'),
            url(r'^clone/(?P<id>\d+)/$', self.wrap(self.clone), name='cms_article_clone'),
            url(r'^power/(.+)/$', self.wrap(self.change_power_view), name='cms_article_change_power'),
        ] + urls

    def get_buttons(self, request, object_id):
        buttons = super(ArticleAdmin, self).get_buttons(request, object_id)
        if object_id:
            buttons.append(
                PowerButton(url=reverse('admin:cms_article_clone', args=(object_id,)), label='Duplicar Artigo'))
            buttons.append(PowerButton(
                url="%s?article__id__exact=%s" % (reverse('admin:cms_articlearchive_changelist'), object_id),
                label='Versões'))
            buttons.append(PowerButton(url="javascript://", attrs={'class': 'button-chamada'}, label='Chamada'))
        return buttons

    def reset_views(self, request, queryset):
        num_oper = 0
        for rec in queryset:
            rec.views = 0
            rec.conversions = 0
            rec.save()
            num_oper += 1
        self.message_user(request, 'Artigos reiniciados: %d ' % num_oper)

    reset_views.short_description = 'Apagar número de visualizações e conversões'

    def export_article(self, request, queryset):
        # refactor da rotina
        name_file = 'Backup_Artigos_' + str(datetime.now())

        if not os.path.exists(
                os.path.join(settings.MEDIA_ROOT, 'uploads', 'backup')):  # Cria a pasta uplods senao tiver criada
            os.mkdir(os.path.join(settings.MEDIA_ROOT, 'uploads', 'backup'))

        myfile = open("%s.zip" % os.path.join(settings.MEDIA_ROOT, 'uploads', 'backup', name_file), "wb")  # cria o zip
        zip = zipfile.ZipFile(myfile, "w", zipfile.ZIP_DEFLATED)
        sections = []

        # incluindo imgs na lista
        imgs = []
        for article in queryset:
            if article.content:
                soup = BeautifulSoup(article.content)
                images = soup.findAll('img')
                for image in images:
                    if image['src']:
                        img = str(image['src'])
                        if img and img.startswith('/media'):
                            imgs.append(img)

            if article.og_image:  # include og_image ao zip
                p = os.path.join(settings.MEDIA_ROOT, article.og_image.path)
                if os.path.exists(p):
                    imgs.append(img)

            if article.header:
                soup = BeautifulSoup(article.header)
                images = soup.findAll('img')
                for image in images:
                    if image['src']:
                        img = str(image['src'])
                        if img and img.startswith('/media'):
                            imgs.append(img)

        serializers = CustomSerializer()
        artigos = serializers.serialize(queryset, indent=4, use_natural_foreign_keys=True, fields=(
            'title', 'slug', 'header', 'content', 'articles', 'author', 'keywords', 'is_active', 'og_title', 'og_image',
            'sections', ''))

        # include article
        info = zipfile.ZipInfo()
        info.filename = "articles.json"
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = (0o644 << 16)
        info.date_time = datetime.now().timetuple()
        zip.writestr(info, artigos)
        #
        # #include sections
        # info = zipfile.ZipInfo()
        # info.filename = "sections.json"
        # info.compress_type = zipfile.ZIP_DEFLATED
        # info.external_attr = (0644 << 16)
        # info.date_time = datetime.now().timetuple()
        # zip.writestr(info, sections)

        # include imgs
        for img in set(imgs):
            path = settings.BASE_DIR + img
            if os.path.exists(path):
                zip.write(path, os.path.basename(path))

        # close zip and file
        zip.close()
        myfile.close()

        FileDownload.objects.get_or_create(title=article.title, file=os.path.join('uploads/backup', name_file + '.zip'),
                                           article=article)

        messages.success(request, 'Exportação realizada com sucesso')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('admin:cms_recurso_changelist')))

    export_article.short_description = 'Exportar Artigos'

    def save_model(self, request, obj, form, change):
        # Versionamento
        if change:
            ant = Article.objects.get(pk=obj.pk)
            version = ArticleArchive(
                article=obj,
                user=request.user
            )
            if ant.header != obj.header:
                version.header = obj.header
                version.save()
            if ant.content != obj.content:
                version.content = obj.content
                version.save()

        if not change:
            obj.author = request.user
            obj.save()

            # Versionamento
            ArticleArchive.objects.create(
                article=obj,
                header=obj.header,
                content=obj.content,
                user=request.user
            )
        return super(ArticleAdmin, self).save_model(request, obj, form, change)


admin.site.register(Article, ArticleAdmin)


class ArticleArchiveAdmin(PowerModelAdmin):
    list_display = ['article', 'updated_at', 'user', ]
    date_hierarchy = 'updated_at'
    list_filter = ['article', 'updated_at', ]
    multi_search = (
        ('q1', 'Título', ['article__title']),
        ('q2', 'Conteúdo', ['content']),
    )
    readonly_fields = ['article', 'user', 'updated_at', ]

    fieldsets = (
        (None, {
            'fields': ['article', 'user', 'updated_at', 'header', 'content', ]
        }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['header', 'content']:
            kwargs['widget'] = CKEditorUploadingWidget()
        return super(ArticleArchiveAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(ArticleArchive, ArticleArchiveAdmin)


class MenuAdmin(DjangoMpttAdmin):
    list_display = ('name', 'is_active',)
    list_editable = ('is_active',)


admin.site.register(Menu, MenuAdmin)


class EmailAgendadoAdmin(PowerModelAdmin):
    list_display = ('subject', 'to', 'status', 'date')
    date_hierarchy = 'date'
    readonly_fields = ('subject', 'to', 'status', 'date')
    fields = ('subject', 'to', 'status', 'date', 'html')
    actions = ('renviar',)
    multi_search = (
        ('q1', 'Para', ['to']),
        ('q2', 'Assunto', ['subject']),
    )

    class Media:
        js = [
            'tiny_mce/tiny_mce.js',
            'tiny_mce/tiny_mce_settings.js',
        ]

    def renviar(self, request, queryset):
        for q in queryset:
            q.send_email()


admin.site.register(EmailAgendado, EmailAgendadoAdmin)


class RecursoAdmin(PowerModelAdmin):
    list_display = ('recurso', 'ativo',)

    def criar_cloudtags(self, request):
        th = Thread(target=Recurso.get_cloudtags, args=())
        th.start()
        messages.info(request, 'Nuvem de tags criada com sucesso!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('admin:cms_recurso_changelist')))

    def get_urls(self):
        urls_originais = super(RecursoAdmin, self).get_urls()
        urls_customizadas = [
            url(r'^criar-cloudtags/$', self.wrap(self.criar_cloudtags),
                name='cms_recurso_criar_cloudtags'),
        ]
        return urls_customizadas + urls_originais

    def get_buttons(self, request, object_id):
        buttons = super(RecursoAdmin, self).get_buttons(request, object_id)
        obj = self.get_object(request, object_id)
        if obj and obj.recurso in ('TAGS', 'TAGS-EXC'):
            buttons.append(PowerButton(url=reverse('admin:cms_recurso_criar_cloudtags'), label='Criar nuvem de tags'))
        return buttons


admin.site.register(Recurso, RecursoAdmin)


class ThemeAdmin(PowerModelAdmin):
    list_display = ('name', 'example', 'active',)
    multi_search = (
        ('q1', 'Nome', ['name']),
        ('q2', 'Descrição', ['description']),
    )
    fieldsets_add = (
        (None, {'fields': ['name', 'active', 'description', ]}),
        ('Arquivo', {'fields': ['path_name', 'theme', ]}),
    )
    fieldsets_edit = (
        (None, {'fields': ['name', 'path_name', 'active', 'description', ]}),
        ('Arquivos', {'fields': ['treepath', ]}),
    )
    form = ThemeForm

    def get_actions(self, request):
        return []

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.prepopulated_fields = {}
            return ('name', 'treepath',)
        self.prepopulated_fields = {'path_name': ('name',)}
        return super(ThemeAdmin, self).get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.fieldsets_add
        return self.fieldsets_edit

    def get_form(self, request, obj=None, **kwargs):
        defaults = {
            "form": self.form if not obj else forms.ModelForm,
            "fields": flatten_fieldsets(self.get_fieldsets(request, obj)),
            "exclude": self.get_readonly_fields(request, obj),
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        # defaults.update(kwargs)
        return modelform_factory(self.model, **defaults)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.active:
            return False
        return super(ThemeAdmin, self).has_delete_permission(request, obj)

    def backup(self, request, object_id):
        theme = get_object_or_404(Theme, pk=object_id)
        try:
            buffer = io.BytesIO()
            zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
            flag = 0
            for root, dirs, files in os.walk(theme.path):
                flag = 1
                for file in files:
                    zip.write(os.path.join(root, file),
                              os.path.join(root.replace(theme.path, theme.path_name.strip()), file))
            if flag == 0:
                raise Exception('o mesmo nao foi encontrado no caminho espefico: ' + theme.path)
            zip.close()
            buffer.flush()
            ret_zip = buffer.getvalue()
            buffer.close()
            response = HttpResponse(ret_zip, content_type='application/octet-stream')
            response['Content-Disposition'] = 'filename=%s.zip' % theme.path_name.replace('/', '')
            l = LogEntry()
            l.action_time = datetime.now()
            l.user = request.user
            l.content_type_id = ContentType.objects.get_for_model(theme).pk
            l.object_repr = str(theme.name)
            l.object_id = theme.pk
            l.action_flag = True
            l.change_message = 'Backup foi efetuado no tema ' + str(theme.name)
            l.save()
            return response
        except Exception as e:
            messages.error(request, 'Erro ao criar .zip do tema %s' % (e))
            return HttpResponseRedirect(reverse('admin:cms_theme_change', args=(object_id,)))

    def collect_static(self, request, object_id):
        try:
            from django.core import management
            log = management.call_command("collectstatic", interactive=False)
            messages.success(request, log)
        except Exception as e:
            messages.error(request, 'Erro no collectstatic: %s' % e)

        return redirect(reverse('admin:cms_theme_change', args=(object_id,)))

    def get_urls(self):
        urls = super(ThemeAdmin, self).get_urls()
        return [
            url(r'^backup/(?P<object_id>\d+)/$', self.wrap(self.backup), name='cms_theme_backup'),
            url(r'^collect_static/(?P<object_id>\d+)/$', self.wrap(self.collect_static),
                name='cms_theme_collect_static'),
        ] + urls

    def get_buttons(self, request, object_id):
        buttons = super(ThemeAdmin, self).get_buttons(request, object_id)
        if object_id:
            obj = self.get_object(request, object_id)
            buttons.append(
                PowerButton(url='%s?&dir=%s' % (reverse('filebrowser:fb_browse'), obj.media_path()), label='Editar'))
            buttons.append(
                PowerButton(url=reverse('admin:cms_theme_backup', kwargs={'object_id': object_id, }), label='Backup'))
            buttons.append(
                PowerButton(
                    url=reverse('admin:cms_theme_collect_static',
                                kwargs={'object_id': object_id, }),
                    label='Update Site'))
        return buttons


admin.site.register(Theme, ThemeAdmin)


class URLNotFoundAdmin(PowerModelAdmin):
    list_display = ('url', 'count', 'created_at', 'update_at',)
    multi_search = (
        ('q1', 'URL', ['url']),
    )
    fieldsets_add = (
        (None, {'fields': ['url', 'count', 'created_at', 'update_at', ]}),
    )
    readonly_fields = ('url', 'count', 'created_at', 'update_at',)


admin.site.register(URLNotFound, URLNotFoundAdmin)

### Nova tela do Group ###
admin.site.unregister(Group)


class GroupAdminCustom(PowerModelAdmin, GroupAdmin):
    form = CustomGroupForm


admin.site.register(Group, GroupAdminCustom)

### Nova tela do usuário ###
admin.site.unregister(User)


class UserAdminCustom(UserAdmin, PowerModelAdmin):
    change_list_template = 'admin/change_list_multi_search.html'
    change_form_template = 'admin/edit_form.html'
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'groups',)
    readonly_fields = ('last_login', 'date_joined',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    fieldsets_user = (
        (None, {'fields': ('username', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'email',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'groups',)}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    fieldsets_superuser = (
        (None, {'fields': ('username', 'password')}),
        ('Informações pessoais', {'fields': ('first_name', 'last_name', 'email',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',)}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
            return self.fieldsets_superuser
        return self.fieldsets_user


admin.site.register(User, UserAdminCustom)


class LogEntryAdmin(PowerModelAdmin):
    list_filter = ('action_time', 'content_type',)
    multi_search = (
        ('q1', 'Usuário', ['user__username']),
        ('q2', 'Objeto', ['object_repr'])
    )
    list_display = ('action_time', 'content_type', 'tipo', 'object_repr', 'user')
    fields = (
        'action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'tipo', 'change_message')
    readonly_fields = (
        'action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'tipo', 'change_message')
    list_per_page = 20

    def tipo(self, obj):
        if obj.is_addition():
            return "Adicionado"
        elif obj.is_change():
            return "Modificado"
        elif obj.is_deletion():
            return "Deletado"


admin.site.register(LogEntry, LogEntryAdmin)
