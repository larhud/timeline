import os
import csv
from io import TextIOWrapper
from datetime import datetime, date

import requests
import hashlib
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

from base.forms import FormImportacaoCSV, IntervaloNoticias, FormBusca, FormBuscaTimeLine
from base.models import Noticia, Termo, Assunto, URL_MAX_LENGTH

from contamehistorias.datasources.webarchive import ArquivoPT


# def testContame(request):
#     requisicao = requests.get("http://127.0.0.1:8000/pesquisa")
#     registro = requisicao.json()
#     #print(registro)
#
#
#     query = 'Rogerio ceni'
#
#     domains = []
#     for k in registro:
#         domains.append(k)
#     print(domains)

# params = {'domains': domains,
#           'from': datetime(year=2016, month=3, day=1),
#           'to': datetime(year=2022, month=1, day=10)}
#
#
#
# apt = ArquivoPT()
# busca = []
# search_result = apt.getResult(query=query, **params)
# for k in search_result:
#     busca.append(k.headline)
#     print(f'teste{busca}')
# # for x in search_result:
# #     print(x.datetime)
# #     print(x.domain)
# #     print(x.headline)
# #     print(x.url)
# #     print()
# context ={
#     'search_result': search_result
# }
#
# return render(request, 'testContame.html', context=context)
#
# Rotina de Busca arquivo.pt
#
def api_arquivopt(request):
    requisicao = requests.get("http://127.0.0.1:8000/pesquisa")
    registro = requisicao.json()
    # print(registro)

    query = 'Bolsonaro'

    domains = []
    totNoticia = 0
    for k in registro['events']:
        domains.append(k['media']['url'])
        totNoticia = totNoticia + 1
    print(f'total = {totNoticia}')

    params = {'domains': domains,
              'from': datetime(year=2016, month=3, day=1),
              'to': datetime(year=2022, month=1, day=10)}

    # print(params)
    apt = ArquivoPT()
    # #busca1 = []
    # print(apt)
    # search_result = apt.getResult(query=query)
    search_result = apt.getResult(query=query, **params)
    # print(search_result)
    for x in search_result:
        print(x.datetime)
        print(x.domain)
        print(x.headline)
        print(x.url)
        print()
    # #_______________________________________________
    busca = ''
    form = FormBusca(request.POST or None, request.FILES or None)
    if request.method == 'POST':

        if form.is_valid():
            busca = form.cleaned_data['busca']
            try:
                termo = Termo.objects.get(termo=busca)
            except Termo.DoesNotExist:
                termo = Termo.objects.create(termo=busca)
                termo.save()
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
                        dt=datetime.strptime(k['tstamp'][:8], '%Y%m%d'),
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


def importacaoCSV(request):
    log_output = None
    form = FormImportacaoCSV(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            texto = form.cleaned_data['arquivo']
            timeline = form.cleaned_data['timeline'].upper()
            termo, _ = Termo.objects.get_or_create(termo=timeline)
            erros = []
            csv_file = TextIOWrapper(texto, encoding='utf-8')
            reader = csv.DictReader(csv_file, delimiter=',')
            tot_linhas = 0
            tot_alteradas = 0
            tot_incluidas = 0
            for linha in reader:
                tot_linhas += 1
                print(tot_linhas)
                url = linha['Media Caption'].split('#')[0]
                if len(url) > URL_MAX_LENGTH:
                    erros.append('Tamanho da URL inválido - linha(%d)' % tot_linhas)
                    continue

                if not url:
                    erros.append('URL em branco - linha (%d)' % tot_linhas)
                    continue

                try:
                    id_externo = int(linha['ID'])
                except:
                    erros.append('ID em branco ou não numérico - linha (%d)' % tot_linhas)
                    continue

                try:
                    ano = linha['Year']
                    mes = linha['Month']
                    dia = linha['Day']
                    dt = datetime.strptime(f"{ano}-{mes}-{dia}", "%Y-%m-%d")
                except ValueError:
                    erros.append(f'Erro ao converter data (linha {tot_linhas})')
                    continue

                url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()

                titulo = linha['Headline']

                try:
                    noticia = Noticia.objects.get(id_externo=id_externo)
                    assunto = noticia.assunto_set.filter(termo=termo, noticia=noticia)
                    found = assunto.count() == 1
                except Noticia.DoesNotExist:
                    found = False

                if found:
                    if url_hash != noticia.url_hash:
                        noticia.url_hash = url_hash
                        noticia.url = url
                        noticia.dt = dt
                        noticia.titulo = titulo
                        noticia.url_valida = False
                        noticia.revisado = False
                        noticia.atualizado = False
                        tot_alteradas += 1
                        print(id_externo)

                        # Verifica se não existe alguma outra URL igual
                        # Se houver e for do mesmo conjunto, indicar o erro
                        dup = Noticia.objects.filter(url_hash=url_hash).exclude(id_externo=id_externo)
                        if dup:
                            erros.append('URL Duplicada: %s (linha %d)' % (url, tot_linhas))
                            temp_hash = hashlib.sha256(str(dup[0].id).encode('utf-8')).hexdigest()
                            dup.update(url_hash=temp_hash, texto_busca='URL duplicada')

                else:
                    try:
                        noticia = Noticia.objects.get(url_hash=url_hash)

                    except Noticia.DoesNotExist:
                        noticia = Noticia(
                            url=url,
                            titulo=titulo,
                            id_externo=id_externo,
                            dt=dt)
                        tot_incluidas += 1

                try:
                    noticia.texto = linha['Text']
                    if linha['Media'][0:4] == 'http':
                        if noticia.media != linha['Media']:
                            noticia.imagem = None
                        noticia.media = linha['Media']
                    else:
                        erros.append('URL da imagem inválida (id_externo %d)' % id_externo)
                    noticia.fonte = linha['Media Credit']
                    noticia.save()

                    # se já houver assunto cadastrado para esse termo, atualiza o id_externo
                    # senão cria um novo
                    try:
                        assunto = Assunto.objects.get(noticia=noticia, termo=termo)
                        assunto.id_externo = id_externo
                        assunto.save()
                    except Assunto.DoesNotExist:
                        Assunto.objects.create(termo=termo, noticia=noticia, id_externo=id_externo)

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
                messages.warning(request, 'Importação efetuada com erros.')
            else:
                messages.info(request, 'Importação efetuada com sucesso.')
            messages.info(request, '%d notícias incluídas' % tot_incluidas)
            messages.info(request, '%d notícias alteradas' % tot_alteradas)

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


def get_pdf(request, noticia_id):
    return


def timeline(request):
    return render(request, 'timelinejs.html')


def pesquisa(request):
    form = FormBuscaTimeLine(data=request.GET)
    form.is_valid()
    queryset = Noticia.objects.pesquisa(**form.cleaned_data)[:500]
    # Adicionada uma segunda consulta, para retornar os anos ao invés de computá-los com base nos registros limitados
    anos = Noticia.objects.pesquisa(**form.cleaned_data).anos()
    data = {'events': [], 'anos': anos}

    for registro in queryset:
        data['events'].append(
            {
                "media": {
                    "link": registro.url or 'http://erro',
                    "url": registro.imagem or registro.media or 'http://erro'
                },
                "start_date": {
                    "month": registro.dt.month,
                    "day": registro.dt.day,
                    "year": registro.dt.year
                },
                "text": {
                    "headline": """<p>""" + registro.titulo + """</p>""",
                    "text": registro.texto
                },
            }
        )

    # quando solucionar o problema da fonte, vamos incluir o background
    #  "background": {
    #                     "color": "#0075FF"
    #                 }

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

            dI = date.strftime(dtInicial, "%Y-%m-%d")
            dF = date.strftime(dtFinal, "%Y-%m-%d")
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


def nuvem_de_palavras(request):
    form = FormBuscaTimeLine(data=request.GET)
    form.is_valid()
    nuvem = [{'text': i[0], 'weight': i[1]} for i in Noticia.objects.pesquisa(**form.cleaned_data).nuvem()]
    return JsonResponse(nuvem, safe=False)
