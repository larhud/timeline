import csv
import datetime
from io import TextIOWrapper

import requests as requests
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render

from base.forms import FormImportacaoCSV, IntervaloNoticias, FormBusca, FormBuscaTimeLine
from base.models import Noticia, Termo, Assunto


#
# Rotina de Busca arquivo.pt
#
def api_arquivopt(request):
    busca = ''
    form = FormBusca(request.POST or None, request.FILES or None)
    if request.method == 'POST':

        if form.is_valid():
            busca = form.cleaned_data['busca']
            try:
                termo = Termo.objects.get_or_create(termo=busca)
            except Termo.DoesNotExist:
                termo = Termo.objects.create(termo=busca)
                termo.save()
            requisicao = requests.get(f"https://arquivo.pt/textsearch?q={busca}")
            registro = requisicao.json()

            new_registro = []

            for k in registro['response_items']:
                new_registro.append(k)

                try:
                    noticia = Noticia.objects.get(url=k['originalURL'])
                except Noticia.DoesNotExist:
                    noticia = Noticia.objects.create(
                        url=k['originalURL'],
                        titulo=k['title'],
                        dt='2021-02-10',
                        texto=k['linkToExtractedText'],
                        media=k['linkToScreenshot'],
                        fonte=k['linkToOriginalFile'],
                    )
                    noticia.save()

                # Assunto.objects.get_or_create(termo=termo, noticia=noticia)
        messages.info(request, 'Resgistros importados com sucesso')
    context = {
        'form': form,
        'busca': busca
    }

    return render(request, 'busca.html', context=context)


def importacaoVC(request):
    form = FormImportacaoCSV(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            texto = form.cleaned_data['arquivo']
            timeline = form.cleaned_data['timeline']
            termo, _ = Termo.objects.get_or_create(termo=timeline)
            csv_file = TextIOWrapper(texto, encoding='utf-8')
            reader = csv.reader(csv_file, delimiter=',')
            reader.__next__()
            tot_linhas = 0
            tot_erros = 0
            for linha in reader:
                url = linha[13]
                if not url:
                    continue

                titulo = linha[9]
                try:
                    ano = linha[0]
                    mes = linha[1]
                    dia = linha[2]
                    dt = datetime.datetime.strptime(f"{ano}-{mes}-{dia}", "%Y-%m-%d")
                except ValueError:
                    messages.error(request, 'Erro ao converter arquivo na linha %d' % tot_linhas + 1)
                    break

                try:
                    noticia = Noticia.objects.get(url=url)
                except Noticia.DoesNotExist:
                    noticia = Noticia.objects.create(
                        url=url,
                        titulo=titulo,
                        dt=dt)
                try:
                    noticia.texto = linha[10]
                    noticia.media = linha[11]
                    noticia.fonte = linha[12]
                    noticia.save()
                    Assunto.objects.get_or_create(termo=termo, noticia=noticia)
                    tot_linhas += 1
                except Exception as e:
                    print(tot_linhas, linha[11])
                    print(e.__str__())
                    tot_erros += 1

            if tot_erros > 0:
                messages.info(request, 'Importação efetuada com %d erros. %d notícias incluídas' %
                              (tot_erros, tot_linhas))
            else:
                messages.info(request, 'Importação efetuada com sucesso. %d notícias incluídas' % tot_linhas)

    context = {
        'form': form
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
                    "url": registro.media,
                    "media": registro.url + """ <span class="tl-note"><a href="URL">Leia a notícia</a></span>"""
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
