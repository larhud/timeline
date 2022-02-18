import os
import csv
import datetime
from io import TextIOWrapper

import requests
import hashlib
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

from base.forms import FormImportacaoCSV, IntervaloNoticias, FormBusca, FormBuscaTimeLine
from base.models import Noticia, Termo, Assunto, URL_MAX_LENGTH


#
# Rotina de Busca arquivo.pt
#
def api_arquivopt(request):
    busca = ''
    form = FormBusca(request.POST or None, request.FILES or None)
    if request.method == 'POST':

        if form.is_valid():
            busca = form.cleaned_data['busca']
            termo, _ = Termo.objects.get_or_create(termo=busca)
            requisicao = requests.get(f"https://arquivo.pt/textsearch?q={busca}")
            registro = requisicao.json()

            new_registro = []

            for k in registro['response_items']:
                new_registro.append(k)
                if len(k['originalURL']) > URL_MAX_LENGTH:
                    print('URL fora do tamanho:')
                try:
                    noticia = Noticia.objects.get(url=k['originalURL'])
                except Noticia.DoesNotExist:
                    noticia = Noticia.objects.create(
                        url=k['originalURL'],
                        titulo=k['title'],
                        dt=datetime.datetime.strptime(k['tstamp'][:8], '%Y%m%d'),
                        texto=k['linkToExtractedText'],
                        media=k['linkToScreenshot'],
                        fonte=k['linkToOriginalFile'],
                    )
                    noticia.save()

                Assunto.objects.get_or_create(termo=termo, noticia=noticia)

        messages.info(request, 'Resgistros importados com sucesso')
    context = {
        'form': form,
        'busca': busca
    }

    return render(request, 'busca.html', context=context)


def importacaoVC(request):
    log_output = None
    form = FormImportacaoCSV(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            texto = form.cleaned_data['arquivo']
            timeline = form.cleaned_data['timeline']
            termo, _ = Termo.objects.get_or_create(termo=timeline)
            erros = []
            csv_file = TextIOWrapper(texto, encoding='utf-8')
            reader = csv.DictReader(csv_file, delimiter=',')
            tot_linhas = 1
            for linha in reader:
                url = linha['Media Caption'].split('#')[0]
                if len(url) > URL_MAX_LENGTH:
                    erros.append('Tamanho da URL inválido - linha(%d)' % tot_linhas)
                    continue

                if not url:
                    erros.append('URL em branco - linha (%d)' % tot_linhas)
                    continue

                try:
                    ano = linha['Year']
                    mes = linha['Month']
                    dia = linha['Day']
                    dt = datetime.datetime.strptime(f"{ano}-{mes}-{dia}", "%Y-%m-%d")
                except ValueError:
                    erros.append('Erro ao converter data (linha %d)' % tot_linhas)
                    continue

                url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
                titulo = linha['Headline']
                try:
                    noticia = Noticia.objects.get(url_hash=url_hash)
                except Noticia.DoesNotExist:
                    noticia = Noticia(
                        url=url,
                        titulo=titulo,
                        dt=dt)
                try:
                    noticia.texto = linha['Text']
                    if linha['Media'][0:4] == 'http':
                        noticia.media = linha['Media']
                    else:
                        erros.append('URL da imagem inválida (linha %d)' % tot_linhas)
                    noticia.fonte = linha['Media Credit']
                    noticia.save()
                    Assunto.objects.get_or_create(termo=termo, noticia=noticia)
                    tot_linhas += 1
                except Exception as e:
                    erros.append('Erro desconhecido na URL: %s (linha %d)' % (url, tot_linhas))
                    erros.append(e.__str__())
                    continue

            if len(erros) > 0:
                log_output = 'erro_importacao.log'
                path_file = os.path.join(settings.MEDIA_ROOT, log_output)
                file_log = open(path_file, mode='w', encoding='utf-8')
                file_log.writelines("%s\n" % line for line in erros)
                file_log.close()
                messages.warning(request, 'Importação efetuada erros. %d notícias incluídas' % tot_linhas)
            else:
                messages.info(request, 'Importação efetuada com sucesso. %d notícias incluídas' % tot_linhas)

    context = {
        'form': form,
        'error': os.path.join(settings.MEDIA_URL, log_output) if log_output else None
    }
    return render(request, 'import_vc.html', context)


def noticiaId(request, noticia_id):
    noticia = Noticia.objects.get(pk=noticia_id)

    return JsonResponse({
        'dt': noticia.dt,
        'titulo': noticia.titulo,
        'texto': noticia.texto,
        'url': noticia.url,
        'media': noticia.media,
        'fonte': noticia.fonte,
    })


def timeline(request):
    return render(request, 'timelinejs.html')


def pesquisa(request):
    form = FormBuscaTimeLine(data=request.GET)
    form.is_valid()
    queryset = Noticia.objects.pesquisa(**form.cleaned_data)[:500]
    # Adicionada uma segunda consulta, para retornar os anos ao invés de computá-los com base nos registros limitados
    anos = list(Noticia.objects.pesquisa(**form.cleaned_data).anos())
    data = {'events': [], 'nuvem': [], 'anos': anos}
    # TODO: Popular nuvem de palavras
    for registro in queryset:
        data['events'].append(
            {
                "media": {
                    "link": registro.url or 'http://erro',
                    "url": registro.media or 'http://erro'
                },
                "start_date": {
                    "month": registro.dt.month,
                    "day": registro.dt.day,
                    "year": registro.dt.year
                },
                "text": {
                    "headline": """<p>""" + registro.titulo + """</p>""",
                    "text": registro.texto
                }
            }
        )

    return JsonResponse(data, safe=False)


def filtro(request):
    form = IntervaloNoticias(request.POST or None, request.FILES or None)

    data = {
        'noticia': []
    }
    if request.method == 'POST':

        if form.is_valid():
            dtInicial = form.cleaned_data['dataInicial']
            dtFinal = form.cleaned_data['dataFinal']

            dI = datetime.date.strftime(dtInicial, "%Y-%m-%d")
            dF = datetime.date.strftime(dtFinal, "%Y-%m-%d")
            filtro = Noticia.objects.filter(dt__gte=dI, dt__lte=dF)

            for registro in filtro:
                data['noticia'].append({
                    'dt': registro.dt,
                    'titulo': registro.titulo
                })

            messages.info(request, 'Filtro atualizado')
        else:
            messages.error(request, 'Erro ao filtrar as notícias')
    context = {
        'form': form,
        'data': data['noticia']
    }
    return render(request, 'pesquisa_data.html', context)
