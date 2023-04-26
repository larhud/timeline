# coding: utf-8
from powercms.crm.views import ContatoView
from django.urls import re_path

urlpatterns = [
    re_path(r'^contato/$', ContatoView.as_view(), name='contato'),
    re_path(r'^cadastro/$', ContatoView.as_view(), name='cadastro'),
]
