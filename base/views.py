import csv
import datetime
import json

from io import TextIOWrapper
from urllib import request

import serializers as serializers
from django.contrib import messages
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, DetailView
import urllib.parse as urlparse
from urllib.parse import parse_qs
from django.views.generic.base import ContextMixin, View

from django_powercms.cms.email import sendmail
from django_powercms.utils.models import LogObject

from base.forms import FormImportacaoCSV, IntervaloNoticias
from base.models import Noticia, Termo, Assunto


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
                        dt=dt,
                        texto=linha[10],
                        media=linha[11],
                        fonte=linha[12],
                    )
                    noticia.save()
                    tot_linhas += 1
                Assunto.objects.get_or_create(termo=termo, noticia=noticia)

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

def govbr(request):

    resultado = []
    queryset = Noticia.objects.filter(url__contains='gov.br')
    data = {
        'events': []
    }
    for registro in queryset:
        data['events'].append(
            {
                "media": {
                    "url": registro.media,
                },
                "start_date": {
                    "month": registro.dt.month,
                    "day": registro.dt.day,
                    "year": registro.dt.year
                },
                "text": {
                    "headline": registro.titulo,
                    "text": registro.texto
                }
            }
        )

    return JsonResponse(data, safe=False)

def home(request):
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
