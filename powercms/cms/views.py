# coding: utf-8
import json
import json as simplejson
import mimetypes
import os
import sys
import zipfile

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.http import base36_to_int
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.defaults import page_not_found
from django.views.generic import DetailView, TemplateView, View, FormView

from powercms.cms.models import Article, Section, URLMigrate, FileDownload, Recurso, Permissao, \
    GroupType, GroupItem, EmailAgendado, URLNotFound, SectionItem
from .forms import ArticleCommentForm, UpdateForm, CMSUserCreationForm


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class UpdateView(LoginRequiredMixin, View):
    title = u'Atualizar PowerCMS'
    form_class = UpdateForm
    template_name = 'admin/cms/update.html'

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST)
        if form.is_valid():
            version = form.cleaned_data.get('version')
            os.system('git pull')
            if version:
                os.system('git checkout %s' % version)
            os.system("%(PROJECT_DIR)s/../../bin/python %(PROJECT_DIR)s/../manage.py syncdb" % {
                'PROJECT_DIR': settings.BASE_DIR,
            })
            os.system("%(PROJECT_DIR)s/../../bin/python %(PROJECT_DIR)s/../manage.py migrate" % {
                'PROJECT_DIR': settings.BASE_DIR,
            })
            os.system("%(PROJECT_DIR)s/../../bin/python %(PROJECT_DIR)s/../manage.py syncdb" % {
                'PROJECT_DIR': settings.BASE_DIR,
            })
            os.popen('supervisorctl restart %s' % settings.BASE_DIR.split('/')[-2])
            messages.info(self.request, u'Sistema atualizado com sucesso!')
        return render(self.request, self.template_name, {
            'form': form,
            'title': self.title,
        })

    def get(self, *args, **kwargs):
        form = self.form_class()
        return render(self.request, self.template_name, {
            'form': form,
            'title': self.title,
        })


class ArticleDetailView(DetailView):
    model = Article
    form = ArticleCommentForm

    def get_template_names(self):
        templates = []
        for section in self.object.sections.all():
            templates.append('%s/article.html' % section.slug)
            templates.append('%s/%s.html' % (section.slug, self.object.slug,))
        templates.append('article/%s.html' % self.object.slug)
        templates.append('article.html')
        return templates

    def get_context_data(self, **kwargs):
        form = self.form()
        if self.request.method == 'POST':
            form = self.form(self.request.POST, initial={'article': self.object, })
            if form.is_valid() and self.object.allow_comments in ('A', 'P'):
                form.instance.article = self.object
                form.save()
                form.sendemail()
                form = self.form()
                messages.info(self.request, u'Comentário enviado!')
            else:
                messages.error(self.request, u'Corrija os erros abaixo!')
        return {
            'article': self.object,
            'form': form,
        }

    def post(self, *args, **kwargs):
        if self.request.POST.get('action') == 'like':
            self.object = self.get_object()
            self.object.likes += 1
            self.object.save()
            return HttpResponse(simplejson.dumps({'likes': self.object.likes}), mimetype='application/json')
        return self.get(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        html_content = render_to_string(self.get_template_names(), {**context}, request=self.request)

        if self.request.user.is_authenticated and self.request.user.is_superuser or self.request.user.groups.filter(name=u'Editor').exists():
            html_content += u'''
                <div id="admin-article-edit" style="background: rgba(255, 255, 255, 0.8);width: 200px;padding: 7px 7px 7px 15px;right: 5px;position: fixed;top: 7px;z-index: 9999999;border: 1px #999 solid;border-radius: 5px;">
                    <a style="color: #444;background: url(/static/cms/imgs/if_pencil_1891403.png) center left no-repeat;padding-left: 25px;font-style: italic;font-weight:  bold;" href="%s">Editar</a>
                </div>''' % reverse('admin:cms_article_change', args=(self.object.pk, ))
        response = HttpResponse(html_content)

        # Redirecionar para a home se: A sessão tem permissão e o usuário não está nesse grupo
        if not self.object.have_perm(self.request.user):
            messages.error(self.request, u'Você não tem permissão para acessar esse artigo!')
            return HttpResponseRedirect(reverse('home'))
        self.object.views += 1
        self.object.save()
        return response


class SectionDetailView(DetailView):
    model = Section

    def get_template_names(self):
        if self.object.template:
            return [self.object.template, ]
        return [
            'section/%s.html' % self.object.slug,
            '%s/section.html' % self.object.slug,
            'section.html',
        ]

    def get_context_data(self, **kwargs):
        articles_list = []
        for article in self.object.get_articles():
            if article.have_perm(self.request.user):
                articles_list.append(article)

        paginator = Paginator(articles_list, 5)

        page = self.request.GET.get('page')
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
        return {
            'section': self.object,
            'articles': articles,
        }


    def get(self, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        html_content = render_to_string(self.get_template_names(), {**context}, request=self.request)

        if self.request.user.is_authenticated and self.request.user.is_superuser or self.request.user.groups.filter(name=u'Editor').exists():
            html_content += u'''
                <div id="admin-article-edit" style="background: rgba(255, 255, 255, 0.8);width: 200px;padding: 7px 7px 7px 15px;right: 5px;position: fixed;top: 7px;z-index: 9999999;border: 1px #999 solid;border-radius: 5px;">
                    <a style="color: #444;background: url(/static/cms/imgs/if_pencil_1891403.png) center left no-repeat;padding-left: 25px;font-style: italic;font-weight:  bold;" href="%s">Editar</a>
                </div>''' % reverse('admin:cms_section_change', args=(self.object.pk, ))
        response = HttpResponse(html_content)

        # Redirecionar para a home se: A sessão tem permissão e o usuário não está nesse grupo
        if not self.object.have_perm(self.request.user):
            messages.error(self.request, u'Você não tem permissão para acessar essa sessão!')
            return HttpResponseRedirect(reverse('home'))
        self.object.views += 1
        self.object.save()
        return response


class HomeView(TemplateView):
    template_name = 'home.html'

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        html_content = render_to_string(self.get_template_names(), {**context}, request=self.request)

        if self.request.user.is_authenticated and self.request.user.is_superuser or self.request.user.groups.filter(name=u'Editor').exists():
            try:
                html_content += u'''
                    <div id="admin-article-edit" style="background: rgba(255, 255, 255, 0.8);width: 200px;padding: 7px 7px 7px 15px;right: 5px;position: fixed;top: 7px;z-index: 9999999;border: 1px #999 solid;border-radius: 5px;">
                        <a style="color: #444;background: url(/static/cms/imgs/if_pencil_1891403.png) center left no-repeat;padding-left: 25px;font-style: italic;font-weight:  bold;" href="%s">Editar</a>
                    </div>''' % reverse('admin:cms_section_change', args=(Section.objects.get(slug='home').pk, ))
            except Section.DoesNotExist: pass
        return HttpResponse(html_content)


class LinkConversionView(View):
    def get(self, request, *args, **kwargs):
        if not 'next' in request.GET:
            raise Http404

        if 'section_slug' in kwargs:
            section = get_object_or_404(Section, slug=kwargs.get('section_slug'))
            section.conversions += 1
            section.save()
        elif 'article_slug' in kwargs:
            article = get_object_or_404(Article, slug=kwargs.get('article_slug'))
            article.conversions += 1
            article.save()

        next = request.GET.get('next')
        if not 'http' in next:
            next = 'http://%s' % next
        return redirect(next)


class URLMigrateView(View):
    def get(self, request, old_url, *args, **kwargs):
        url = get_object_or_404(URLMigrate, old_url=old_url)
        url.views += 1
        url.save()
        if url.redirect_type == 'M':
            return HttpResponsePermanentRedirect(url.new_url)
        return HttpResponseRedirect(url.new_url)


class FileDownloadView(View):
    def get(self, request, file_uuid, *args, **kwargs):
        file_download = get_object_or_404(FileDownload, uuid=file_uuid)
        if file_download.is_expired():
            raise Http404()

        file_download.count += 1
        file_download.save()
        try:
            mimetype = mimetypes.guess_type(file_download.file.path)[0]
        except NotImplementedError:
            mimetype = mimetypes.guess_type(file_download.file.name)[0]
        return HttpResponse(file_download.file.read(), content_type=mimetype)


class SearchView(TemplateView):
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q')
        results_list = []
        if q:
            termo = q.lower()
            articles_list = Article.objects.filter(is_active=True, search__contains=termo)
            for article in articles_list:
                if article.have_perm(self.request.user):
                    results_list.append({
                        'title': article.title,
                        'object': article,
                    })
            results_list = sorted(results_list, key=lambda k: k['title'])

        paginator = Paginator(results_list, 5)
        page = self.request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)
        return {
            'q': q,
            'results': results,
        }


class RobotsView(View):
    def get(self, request, *args, **kwargs):
        robots = Recurso.objects.get_or_create(recurso='ROBOTS')[0]
        if robots.ativo:
            return HttpResponse(u'User-agent: *\nAllow: *', content_type='text/plain')
        return HttpResponse(u'User-agent: *\nDisallow: *', content_type='text/plain')


class SignupView(FormView):
    form_class = CMSUserCreationForm
    template_name = 'auth/signup.html'
    template_name_done = 'auth/signup_done.html'

    def form_valid(self, form):
        form.save()
        form = self.form_class()
        return self.response_class(
            request=self.request,
            template=self.template_name_done,
            context=self.get_context_data(form=form),
        )



@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='auth/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect='/',
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb36 is not None and token is not None # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                user = authenticate(username=user.username, password=form.cleaned_data['new_password1'])
                auth_login(request, user)
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def signup_filter(request, grouptype_id, groupitem_id):
    pai = get_object_or_404(GroupItem, pk=groupitem_id)
    grouptype = get_object_or_404(GroupType, pk=grouptype_id)

    results = []
    pai_sessoes_ids = Permissao.objects.filter(group=pai.group).values_list('section', flat=True)
    for item in grouptype.groupitem_set.all():
        if Permissao.objects.filter(group=item.group, section__pk__in=pai_sessoes_ids).exists():
            results.append(item)

    result = []
    for item in results:
        result.append({'pk': item.pk, 'display': item})
    json = simplejson.dumps(result)
    return HttpResponse(json, mimetype='application/json')


def status(request):
    json = {}
    # HD
    devices_data = os.popen('df').read().split('\n')
    header = devices_data[0].split()
    for device in devices_data[1:]:
        if device:
            data = [int(data) if data.isdigit() else data for data in device.split()[1:]]
            json[device.split()[0]] = dict(zip(header[1:], data))
    # Memory
    memory_data = os.popen('free').read().split('\n')
    header = memory_data[0].split()
    for memory in memory_data[1:]:
        if memory:
            data = [int(data) if data.isdigit() else data for data in memory.split()[1:]]
            json[memory.split()[0]] = dict(zip(header, data))
        # Email
    status_email = 0 # Enabled
    try:
        if EmailAgendado.objects.latest('pk').status == 'E':
            status_email = 1 # Com erro
        elif not Recurso.objects.get_or_create(recurso='EMAIL')[0].ativo:
            status_email = 2 # Disable
    except EmailAgendado.DoesNotExist: pass
    json['mail'] = {
        'Available': status_email
    }
    return HttpResponse(simplejson.dumps(json), content_type="application/json")


def page_not_found_view(request, exception=None):
    url = request.build_absolute_uri()
    if not url.endswith('.php'):
        notfound = URLNotFound.objects.get_or_create(url=url)[0]
        notfound.count += 1
        notfound.save()
    return page_not_found(request, exception, template_name='404.html')

def handler500(request):
    return render(request, '500.html', status=500)


class ImportArticle(LoginRequiredMixin, TemplateView):
    login_url = '/admin/login/'
    template_name = 'import_article.html'


    def test_slug(self, slug, Model): #testando slugs
        q = Model.objects.filter(slug=slug)
        if q:
            slug = '%s-novo' % q.get().slug
            return self.test_slug(slug, Model)

        return slug

    def post(self, form):
        f = self.request.FILES['file']
        nao_incluidas = []
        logs = []
        try:
            zip = zipfile.ZipFile(f, 'r')
            read = zip.read('articles.json')
            articles = json.loads(read.decode())
        except Exception as erro:
            return JsonResponse({'is_valid': False,'msg': {'text': 'Arquivo inválido %s' % str(erro), 'type': 'danger'}})
        try:
            for article in articles:
                title = article['fields']['title']
                try:
                    user = User.objects.get(username=article['fields']['author'][0])
                except Exception:
                    user = User.objects.get_or_create(username='sys')[0]

                header = article['fields']['header']
                content = article['fields']['content']
                keywords = article['fields']['keywords']
                og_title = article['fields']['og_title']
                og_image = article['fields']['og_image']
                sections = article['fields']['sections']
                name = os.path.basename(og_image)
                if name:
                    path_og_image = os.path.join(settings.MEDIA_ROOT, og_image)

                    if not os.path.exists(path_og_image):
                        try:
                            zip.extract(name, os.path.dirname(path_og_image))
                            logs.append({'file': name, 'slug': '#',
                                     'c': path_og_image, 'is_include': True, 'type': 'Imagem', 'add': 'glyphicon glyphicon-ok'})
                        except:
                            None
                    else:
                        nao_incluidas.append(name)
                        logs.append({'file': name, 'slug': '#',
                                 'c': path_og_image, 'is_include': False, 'type': 'Imagem', 'add': 'glyphicon glyphicon-remove'})

                imgs = self.is_path(content)  # testando se todas as imgs jÃ¡ existem
                imgs += self.is_path(header)
                for img in imgs:
                    is_path = img.get('exist')
                    path = img.get('path')
                    name = os.path.basename(path)
                    path = os.path.dirname(path)
                    if not is_path:  # not existir
                        try:
                            zip.extract(name, settings.PROJECT_DIR + path)
                            logs.append({'file': name, 'slug': '#',
                                         'c': img.get('path'), 'is_include': True, 'type': 'Imagem', 'add': 'glyphicon glyphicon-ok'})
                        except:
                            None
                    else:
                        nao_incluidas.append(name)
                        logs.append({'file': name, 'slug': '#',
                                     'c': img.get('path'), 'is_include': False, 'type': 'Imagem', 'add': 'glyphicon glyphicon-remove'})

                slug = self.test_slug(article['fields']['slug'], Article)

                obj_article = Article.objects.create(slug=slug, title=title, header=header,
                                                                           content=content, author=user, keywords=keywords,
                                                                           og_title=og_title, og_image=og_image)

                logs.append({'file': obj_article.title, 'slug': obj_article.slug,'c': '/admin/cms/article/%s/change/' %obj_article.pk, 'type': 'Artigo', 'add': 'glyphicon glyphicon-ok'})
                for section in sections:
                    title = section['fields']['title']
                    header = section['fields']['header']
                    template = section['fields']['template']
                    slug = section['fields']['slug']
                    obj_section = Section.objects.filter(slug=slug)
                    if obj_section:
                        obj_section = obj_section[0]
                        logs.append({'file': obj_section.title, 'slug': 'section/%s' % obj_section.slug,
                                     'c': '/admin/cms/section/%s/change/' % obj_section.pk, 'type': 'Sessão',
                                     'add': 'glyphicon glyphicon-remove'})

                    else:
                        obj_section = Section.objects.create(slug=slug, title=title, header=header,
                                                             template=template)
                        logs.append({'file': obj_section.title, 'slug': 'section/%s'% obj_section.slug,
                                          'c': '/admin/cms/section/%s/change/' % obj_section.pk, 'type': 'Sessão', 'add': 'glyphicon glyphicon-ok'})


                    SectionItem.objects.get_or_create(article=obj_article, section=obj_section)

                    LogEntry.objects.log_action(
                        user_id=self.request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(obj_section).pk,
                        object_id=obj_section.pk,
                        object_repr=obj_section.serializable_value('title'),
                        action_flag=ADDITION,
                    )

                imgs = self.is_path(header)  # testando se todas as imgs já¡ existem
                for img in imgs:
                    is_path = img.get('exist')
                    path = img.get('path')
                    name = os.path.basename(path)
                    path = os.path.dirname(path)
                    if not is_path:  # not existir
                        try:
                            zip.extract(name, settings.PROJECT_DIR + path)
                            logs.append({'file': name, 'slug': '#',
                                         'c': img.get('path'), 'is_include': True, 'type': 'Imagem', 'add': 'glyphicon glyphicon-ok'})
                        except:
                            None
                    else:
                        nao_incluidas.append(name)
                        logs.append({'file': name, 'slug': '#',
                                     'c': img.get('path'), 'is_include': False, 'type': 'Imagem', 'add': 'glyphicon glyphicon-remove'})

                if len(nao_incluidas) > 1:
                    LogEntry.objects.log_action(
                        user_id=self.request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(obj_article).pk,
                        object_id=obj_article.pk,
                        object_repr=json.dumps(nao_incluidas),
                        action_flag=3,
                        change_message='Imagens não adicionadas, pois já existem no path.'
                    )

                LogEntry.objects.log_action(
                                user_id=self.request.user.pk,
                                content_type_id=ContentType.objects.get_for_model(obj_article).pk,
                                object_id=obj_article.pk,
                                object_repr=obj_article.serializable_value('title'),
                                action_flag=ADDITION,
                        )

            return JsonResponse({'is_valid': True, 'host': self.request.META['HTTP_ORIGIN'], 'logs': logs, 'msg': {'text': 'Artigo adicionado com sucesso', 'type': 'success'}} )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return JsonResponse({'is_valid': False, 'msg': {'text': 'Error: %s' % e, 'type': 'danger'}})

    def is_path(self, image):
        soup = BeautifulSoup(image or '')
        images = soup.findAll('img')
        imgs = []
        for image in images:
            path = image['src']
            if path.startswith('/media'):
                if os.path.exists(settings.BASE_DIR + image['src']):
                    imgs.append({'exist': True, 'path': path})
                else:
                    imgs.append({'exist': False, 'path': path})

        return imgs