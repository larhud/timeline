from urllib import request

from django.urls import path
from . import views

urlpatterns = [
    path('arquivo/', views.importacaoVC),
    path('noticias/<int:noticia_id>', views.noticiaId),
    path('timeline/', views.timeline),
    path('govbr/', views.govbr),
    path('home/', views.home, name='filtro'),

    path('busca/', views.busca)

]
