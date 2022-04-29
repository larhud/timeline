from django.urls import path
from . import views, api

urlpatterns = [
    path('timeline/<slug:slug>/', views.TimeLinePorTermo.as_view(), name='timeline_por_termo'),
    path('get_pdf/<int:id>', views.get_pdf, name='get_pdf'),
    path('scrap_text/<int:id>', views.scrap_text, name='scrap_text'),
    path('importacao/', views.importacaoCSV),
    path('noticias/<int:noticia_id>', views.noticiaId),
    path('arquivopt/', views.api_arquivopt),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('filtro_data/', views.filtro, name='filtro'),
    path('nuvem-de-palavras/', views.nuvem_de_palavras, name='nuvem_de_palavras'),
    path('arquivo_json/', views.arquivo_json, name='arquivo_json'),
    path('arquivotm/', api.arquivoTM)
]
