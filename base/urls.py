from urllib import request

from django.urls import path
from . import views

urlpatterns = [
    path('arquivo/', views.importacaoVC),
    path('noticias/<int:noticia_id>', views.noticiaId)
]
