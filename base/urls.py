from urllib import request

from django.urls import path
from . import views

urlpatterns = [
    path('importacao/', views.importacaoCSV),
    path('noticias/<int:noticia_id>', views.noticiaId),
    path('arquivopt/', views.api_arquivopt),
    path('timeline/', views.timeline),
    path('get_pdf/<int:id>', views.get_pdf, name='get_pdf'),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('filtro_data/', views.filtro, name='filtro'),
    path('nuvem-de-palavras/', views.nuvem_de_palavras, name='nuvem_de_palavras'),

]
