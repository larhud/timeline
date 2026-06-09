# coding: utf-8
from powercms.cms.sitemap import sitemaps

from powercms.cms.views import *
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, PasswordChangeDoneView, \
       PasswordResetDoneView, PasswordResetCompleteView, LoginView, PasswordResetConfirmView, \
       LogoutView
from django.contrib.sitemaps.views import sitemap
from django.urls import re_path, path, reverse_lazy
from django.views.generic.base import RedirectView

urlpatterns = [
       re_path(r'^update/$', UpdateView.as_view(), name='update'),

       re_path(r'^$', HomeView.as_view(), name='home'),
       re_path(r'^pesquisa/$', SearchView.as_view(), name='search'),
       re_path(r'^section/(?P<slug>[-_\w]+)/$', SectionDetailView.as_view(), name='section'),
       re_path(r'^download/(?P<file_uuid>[-_\w]+)/$', FileDownloadView.as_view(), name='download'),
       re_path(r'^link/a/(?P<article_slug>[-_\w]+)/$', LinkConversionView.as_view(), name='link'),
       re_path(r'^link/s/(?P<section_slug>[-_\w]+)/$', LinkConversionView.as_view(), name='link'),
       re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}),
       re_path(r'^robots\.txt$', RobotsView.as_view(), name="robots"),

       path('login/', LoginView.as_view(template_name='auth/login.html', redirect_field_name='admin'), name='cms_login'),
       re_path(r'^logout/$', LogoutView.as_view(template_name='auth/logout.html'), name='cms_logout'),
       re_path(r'^signup/$', SignupView.as_view(), name='cms_signup'),
       re_path(r'^signup/filter/(?P<grouptype_id>[\d]+)/(?P<groupitem_id>[\d]+)/$', signup_filter, name='signup_filter'),
       path('password_change/', PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='cms_password_change'),
       path('password_change/done/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='cms_password_change_done'),
       path('password_reset/',  PasswordResetView.as_view(template_name='registration/password_reset_form.html',email_template_name='auth/password_reset_email.html'), name='cms_password_reset'),
       path('password_reset/done/', PasswordResetDoneView.as_view(template_name= 'registration/password_reset_done.html'), name='password_reset_done'),
       path('admin/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', success_url=reverse_lazy('cms_password_reset_complete')), name='password_reset_confirm'),
       path('reset/done/', PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='cms_password_reset_complete'),
       re_path(r'^powerpost/$', RedirectView.as_view(url='/admin/cms/article/add-power/'), name="cms_article_powerpost"),
       re_path(r'^status/$', status, name='status'),
       re_path(r'^(?P<slug>[-_\w]+)/$', ArticleDetailView.as_view(), name='article'),
       path('utils/importar-artigo/', ImportArticle.as_view(), name='importar_artigo'),
]