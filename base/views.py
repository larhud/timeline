import csv
import datetime
import time
import json
import os
from collections import Counter

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.db.models import F
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

from base.forms import FormImportacaoVC
from base.models import Noticia, Csv
from base.models import Termo


def importacaoVC(request):
    arq = Noticia.objects.all()
    form = FormImportacaoVC(request.POST or None, request.FILES or None)

    if str(request.method) == 'POST':
        if form.is_valid():
            form.save()
            form = FormImportacaoVC()
            obj = Csv.objects.get()

            with open(obj.file_name.path, 'r') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                reader.__next__()

                for i, linha in enumerate(reader):
                    url = linha[0]
                    titulo = linha[1]
                    dt = linha[2]
                    texto = linha[3]
                    media = linha[4]
                    grupo = linha[5]
                    nuvem = linha[6]
                    atualizado = linha[7]

                    arqui = Noticia.objects.create(
                        url = url,
                        titulo = titulo,
                        dt = dt,
                        texto = texto,
                        media = media,
                        group = grupo,
                        nuvem = nuvem,
                        atualizado = atualizado,

                    )

            arqui.save()

        else:
            messages.error(request, 'Erro ao enviar arquivo')

    context = {
        'form': form
    }
    return render(request, 'import_vc.html', context)
