# from django.conf.urls.defaults import  url
from django.urls import re_path

urlpatterns = [
    '',
    re_path(r'^upload/', 'ckeditor.views.upload', name='ckeditor_upload'),
    re_path(r'^browse/', 'ckeditor.views.browse', name='ckeditor_browse'),
]
