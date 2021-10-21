import csv
import datetime

from io import TextIOWrapper

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, DetailView
import urllib.parse as urlparse
from urllib.parse import parse_qs
from django.views.generic.base import ContextMixin, View

from django_powercms.cms.email import sendmail
from django_powercms.utils.models import LogObject

from base.forms import FormImportacaoCSV
from base.models import Noticia
from base.models import Termo


def importacaoVC(request):
    form = FormImportacaoCSV(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            texto = form.cleaned_data['arquivo']
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

                arqui = Noticia.objects.create(
                    url=url,
                    titulo=titulo,
                    dt=dt,
                    texto=linha[10],
                    media=linha[11],
                    fonte=linha[12]
                )
                arqui.save()
                tot_linhas += 1

            messages.info(request, 'Importação efetuada com sucesso. %d notícias incluídas' % tot_linhas)
        else:
            messages.error(request, 'Erro ao importar o arquivo')

    context = {
        'form': form
    }
    return render(request, 'import_vc.html', context)


def noticiaId(request, noticia_id):
    noticia = Noticia.objects.get(pk=noticia_id)

    return JsonResponse({
        'year': noticia.year,
        'month': noticia.month,
        'day': noticia.day,
        'headline': noticia.headline,
        'text': noticia.text,
        'media': noticia.media,
        'media_credit': noticia.media_credit,
        'media_caption': noticia.media_caption,
        'background': noticia.background
    })
