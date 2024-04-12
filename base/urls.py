from django.urls import path
from . import views, api

urlpatterns = [
    path('timeline/<slug:slug>/', views.TimeLinePorTermo.as_view(), name='timeline_por_termo'),
    path('mensagem/', views.ContatoView.as_view(), name='mensagem'),
    path('get_pdf/<int:id>', views.get_pdf, name='get_pdf'),
    path('upload_pdf/<int:id>', views.upload_pdf, name='upload_pdf'),
    path('scrap_text/<int:id>', views.scrap_text, name='scrap_text'),
    path('scrap_image/<int:id>', views.scrap_image, name='scrap_image'),
    path('importacao/', views.importacaoCSV),
    path('noticias/<int:noticia_id>', views.noticiaId),
    path('arquivopt/', views.api_arquivopt),
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('filtro_data/', views.filtro, name='filtro'),
    path('nuvem-de-palavras/', views.nuvem_de_palavras, name='nuvem_de_palavras'),
    path('arquivo_json/', views.arquivo_csv, name='arquivo_csv'),
    path('arquivotm/', api.arquivoTM),
    path('lista-de-fontes/<int:termo>', views.lista_de_fontes, name='lista_de_fontes'),
    path('lista-de-termos/', views.lista_de_termos, name='lista_de_termos'),
    path('novo-contato/', views.novo_contato, name='novo_contato'),
    path('quebra<int:id>', views.quebra_termo, name='quebra_termo')
]
