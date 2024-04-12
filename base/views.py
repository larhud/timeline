import csv
import hashlib
import os
import json
from datetime import datetime, date, timedelta
from io import TextIOWrapper

import time

import requests
from bs4 import BeautifulSoup

from contamehistorias.datasources.webarchive import ArquivoPT
from contamehistorias.datasources import models, utils
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage

from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseNotAllowed
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import DetailView, TemplateView

from base import save_image
from base.forms import FormImportacaoCSV, IntervaloNoticias, BuscaArquivoPT, FormBuscaTimeLine, ContatoForm
from base.models import Noticia, Termo, Assunto, URL_MAX_LENGTH
from base.management.commands.get_text import extract_text, load_html
from powercms.crm.models import Contato
from timeline.settings import noticia_imagem_path


class TimeLinePorTermo(DetailView):
    """View que vai buscar um termo e apresentar as notícias em uma timeline"""
    template_name = 'timeline-por-termo.html'
    model = Termo
    slug_field = 'slug'


def nuvem_de_palavras(request):
    form = FormBuscaTimeLine(data=request.GET)
    form.is_valid()
    nuvem = [{'text': i[0], 'weight': i[1]} for i in Noticia.objects.pesquisa(**form.cleaned_data).nuvem()]
    return JsonResponse(nuvem, safe=False)


class ContatoView(TemplateView):
    template_name = 'home2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        Contato.objects.get_or_create(
            email=form.cleaned_data.get('email'),
            defaults={'nome': form.cleaned_data.get('nome')}
        )
        form.sendemail()

        messages.info(self.request, u'Contato cadastrado com sucesso!')
        form = self.form_class()

        return self.response_class(
            request=self.request,
            template=self.template_name,
            context=self.get_context_data(form=form),
        )


def api_arquivopt(request):
    busca = ''
    form = BuscaArquivoPT(request.POST or None, request.FILES or None)
    if request.method == 'POST':

        if form.is_valid():
            busca = form.cleaned_data['busca']
            try:
                termo = Termo.objects.get(termo=busca)
            except Termo.DoesNotExist:
                termo = Termo.objects.create(termo=busca)
                termo.save()

            url_busca = f"https://arquivo.pt/textsearch?q={busca}"
            if form.cleaned_data['dtinicial']:
                dt_inicial = form.cleaned_data['dtinicial'].strftime('%Y%m%d')
                url_busca += '&from=' + dt_inicial

            if form.cleaned_data['dtfinal']:
                dt_final = form.cleaned_data['dtfinal'].strftime('%Y%m%d')
                url_busca += '&to=' + dt_final

            tot_lidos = 0
            tot_gravados = 0
            while tot_gravados < 300 and url_busca:
                requisicao = requests.get(url_busca)
                registro = requisicao.json()
                url_busca = registro['next_page']
                for k in registro['response_items']:
                    tot_lidos += 1
                    url = k['originalURL']
                    domain = url.split('/')[2]
                    country = domain.split('.')[-1]
                    if country != 'pt' or len(url) > URL_MAX_LENGTH:
                        continue

                    try:
                        url = k['linkToNoFrame']
                        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
                        titulo = BeautifulSoup(k['title'], features="lxml").text
                        noticia = Noticia.objects.get(url_hash=url_hash)
                        if not noticia.revisado:
                            noticia.titulo = titulo
                    except Noticia.DoesNotExist:
                        noticia = Noticia.objects.create(
                            dt=datetime.strptime(k['tstamp'][:8], '%Y%m%d'),
                            url=url,
                            titulo=titulo,
                            texto=k['snippet'],
                            media=k['linkToScreenshot'],
                            fonte=domain,
                            visivel=True,
                        )
                    noticia.origem = 2
                    noticia.save()
                    Assunto.objects.get_or_create(termo=termo, noticia=noticia)
                    tot_gravados += 1

        messages.info(request, f'{tot_lidos} registros lidos')
        messages.info(request, f'{tot_gravados} registros importados com sucesso')

    context = {
        'form': form,
        'busca': busca
    }

    return render(request, 'busca.html', context)


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
                    noticia = Noticia.objects.get(id_externo=id_externo, assunto__termo=termo)
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
                        noticia.origem = 1
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
                            dt=dt,
                            visivel=True)
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

                    if len(linha['Texto completo raspado']) > 0 and not noticia.revisado:
                        noticia.texto_completo = linha['Texto completo raspado']
                        noticia.atualizado = True
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


def get_pdf(request, id):
    filename = f'{settings.MEDIA_ROOT}/pdf/{id}.pdf'
    if os.path.exists(filename):
        return FileResponse(open(filename, 'rb'), content_type='application/pdf')
    else:
        messages.info(request, f'Arquivo PDF não encontrado: {id}.pdf')
        return redirect(reverse('admin:base_noticia_change', args=(id,)))


def upload_pdf(request, id):
    filename = f'{settings.MEDIA_ROOT}/pdf/{id}.pdf'
    if os.path.exists(filename):
        return FileResponse(open(filename, 'rb'), content_type='application/pdf')
    else:
        messages.info(request, f'Arquivo PDF não encontrado: {id}.pdf')
        return redirect(reverse('admin:base_noticia_change', args=(id,)))


def scrap_text(request, id):
    noticia = Noticia.objects.get(id=id)
    soup = load_html(noticia.url, id, use_cache=True)
    if soup:
        if not noticia.titulo:
            tag = soup.find("meta", property="og:title")
            if tag and tag['content']:
                noticia.titulo = tag['content']
            else:
                tag = soup.find("title")
                if tag:
                    noticia.titulo = tag.text

        if not noticia.media:
            tag = soup.find("meta", property="og:image")
            if tag:
                noticia.media = tag['content'][:100]

        tag = soup.find("meta", property="og:description")
        if tag and not noticia.texto:
            noticia.texto = tag['content']

        if not noticia.revisado:
            noticia.texto_completo = extract_text(soup)
        noticia.atualizado = True
        noticia.save()
    else:
        messages.info(request, 'Não foi possível carregar a URL. Realize a carga manual')
        noticia.url_valida = False
        noticia.atualizado = False
        noticia.save()

    return redirect(reverse('admin:base_noticia_change', args=(id,)))


def scrap_image(request, id):
    noticia = Noticia.objects.get(id=id)
    img_path = noticia_imagem_path()
    file_path = save_image(noticia.media, img_path, noticia.id)
    if file_path:
        noticia.imagem = file_path
        noticia.save()
        messages.info(request, 'Imagem validada e armazenada')
    else:
        messages.error(request, 'Não foi possível carregar a imagem. Verifique a URL da imagem')

    return redirect(reverse('admin:base_noticia_change', args=(id,)))


def timeline(request):
    return render(request, 'timelinejs.html')


def pesquisa(request):
    form = FormBuscaTimeLine(data=request.GET)
    form.is_valid()
    queryset = Noticia.objects.pesquisa(**form.cleaned_data)
    # Adicionada uma segunda consulta, para retornar os anos ao invés de computá-los com base nos registros limitados
    anos = Noticia.objects.pesquisa(**form.cleaned_data).anos()
    data = {'events': [], 'anos': anos}

    for registro in queryset[:200]:
        url = registro.url or 'http://erro'
        data['events'].append(
            {
                "media": {
                    "link": url,
                    "url": registro.imagem_final
                },
                "start_date": {
                    "month": registro.dt.month,
                    "day": registro.dt.day,
                    "year": registro.dt.year
                },
                "text": {
                    "headline": f'<p>{registro.titulo}</p>',
                    "text": f'{registro.texto}<br/><p><b><a href="{url}">{registro.fonte}</a></b></p>'
                },
                "background": {
                    "color": "#0075FF"
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


def arquivo_csv(request):
    form = FormBuscaTimeLine(data=request.GET)
    form.is_valid()
    dataset = Noticia.objects.pesquisa(**form.cleaned_data)

    csv_file = 'dt;titulo;texto;texto_completo;url;media;fonte\n'
    for noticia in dataset.filter(visivel=True):
        if noticia.texto_completo:
            texto = noticia.texto_completo.replace('"', '')
        else:
            texto = ''
        csv_file += '%s;"%s";"%s";"%s";"%s";"%s";"%s"\n' % (
            noticia.dt.strftime('%d/%m/%Y'),
            noticia.titulo,
            noticia.texto,
            texto,
            noticia.url,
            noticia.media,
            noticia.fonte,
        )

    response = HttpResponse(csv_file, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timeline.csv"'
    return response


def arquivo_json(request):
    form = FormBuscaTimeLine(data=request.GET)
    form.is_valid()
    dataset = Noticia.objects.pesquisa(**form.cleaned_data)
    result = []
    for noticia in dataset:
        result.append({
            'dt': noticia.dt.strftime('%d/%m/%Y'),
            'titulo': noticia.titulo,
            'texto': noticia.texto,
            'url': noticia.url,
            'media': noticia.media,
            'fonte': noticia.fonte,
        })

    json_str = json.dumps(result, indent=4, ensure_ascii=False)
    response = HttpResponse(json_str, content_type='application/json')
    response["Content-Disposition"] = 'attachment; filename=export.json'
    return response


# Faz a paginação das fontes das notícias
def lista_de_fontes(request, termo):
    queryset = Assunto.objects.fontes(termo)
    pagina = request.GET.get('page', 1)
    itens_por_pagina = request.GET.get('pageSize', 50)
    paginator = Paginator(queryset, itens_por_pagina)

    try:
        fontes = paginator.page(pagina)
    except PageNotAnInteger:
        fontes = paginator.page(1)
    except InvalidPage:
        fontes = paginator.page(paginator.num_pages)

    result = {
        'num_pages': fontes.paginator.num_pages, 'total': fontes.paginator.count,
        'pagina': pagina, 'items': list(fontes.object_list),
        'fields': {'noticia__fonte': 'Fonte', 'total': 'Total de Notícias', 'invalidos': 'URL Inválidas'}
    }

    return JsonResponse(result)


def lista_de_termos(request):
    queryset = Termo.objects.filter(visivel=True).order_by(request.GET.get('order_by', 'pk'))
    pagina = request.GET.get('pageNumber', 1)
    paginator = Paginator(queryset, request.GET.get('pageSize', 4))

    try:
        termos = paginator.page(pagina)
    except PageNotAnInteger:
        termos = paginator.page(1)
    except InvalidPage:
        termos = paginator.page(paginator.num_pages)

    result = {
        'total': paginator.count,
        'items': [
            {
                'termo': item.termo, 'texto': item.texto_breve, 'imagem': item.url_imagem,
                'url': item.get_absolute_url()
            } for item in termos.object_list
        ]
    }

    return JsonResponse(result)


def novo_contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)

        if form.is_valid():
            form.sendemail()
            data = {'success': ['Contato enviado com sucesso']}
        else:
            data = form.errors
        response = JsonResponse(data)
    else:
        response = HttpResponseNotAllowed(['POST'])

    return response

def quebra_termo(request, id):
    template_name = 'nuvem_crono.html'
    n_slot = 15                             #numero de slots

    result = nuvem_cronologica(id, n_slot)  #resultado da nuvem_crono em JsonResponse

    header = {'header':['Dt Inicial', 'Dt Final', 'Termos']}
    rows = { 'rows': []}

    t_list = []
    for i in range(0, n_slot, 1):
        t_list.append([])

    n_palavras = 10
    for i in range(0, n_slot, 1):
        for j in range(2, (n_palavras+2), 1): #10 palavras
            if (len(result[i]) <= 2): #caso onde a l_result(slot) tem apenas as datas e nao tem noticias
                j += 1
            else:
                t_list[i].append(result[i][j][0])

        rows['rows'].append({
            'dt_inicial': result[i][0],
            'dt_final': result[i][1],
            'termos': t_list[i],
            })

    context = {
        'header': header['header'],
        'rows': rows['rows'],
    }

    return render(request, template_name, context)

def nuvem_cronologica(id, n_slot):

    noticias_termo = Noticia.objects.filter(assunto__termo=id) #noticias do termo passado
    latest_dt = noticias_termo.latest('dt').dt                              #latest date
    earliest_dt = noticias_termo.earliest('dt').dt                          #earliest date

    earliest_datetime = datetime.combine(earliest_dt, datetime.min.time())  #date to datetime
    latest_datetime = datetime.combine(latest_dt, datetime.min.time())      #date to datetime

    earliest_timestamp = datetime.timestamp(earliest_datetime)      #datetime to timestamp
    latest_timestamp = datetime.timestamp(latest_datetime)          #datetime to timestamp

    periodo = latest_timestamp - earliest_timestamp                 #periodo
    tam_slot = periodo/(n_slot)                                #cada slot tem tamanho periodo/(n_slot)

    l_slots = []                                          #lista com a data do inicio e fim de cada slot
    for i in range(0, n_slot, 1):
        l_slots.append([date.fromtimestamp(earliest_timestamp+((i)*tam_slot)) , date.fromtimestamp(earliest_timestamp+((i+1)*tam_slot)) - timedelta(days=1)])

    l_nuvem = []                                          #lista da nuvem de palavras de cada slot
    for i in range(0, n_slot, 1):
        l_nuvem.append(Noticia.objects.pesquisa(datafiltro=l_slots[i]).nuvem())

    n_palavras = 10
    l_result = []                        #lista de slots e suas respectivas nuvems(n_palavras mais acessadas)
    for i in range(0, n_slot, 1):
        var = l_slots[i]
        var[0] = datetime.strftime(var[0], '%d/%m/%Y')
        var[1] = datetime.strftime(var[1], '%d/%m/%Y')
        l_result.append(var)
        for j in range(0, n_palavras, 1):
            if (len(l_nuvem[i]) == 0):      #Caso nao hajam noticias no slot
                j += 1
            else:
                l_result[i].append(l_nuvem[i][j])

    return l_result