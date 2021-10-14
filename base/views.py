import csv
from django.http import JsonResponse
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
    #arq = Noticia.objects.all()
    form = FormImportacaoVC(request.POST or None, request.FILES or None)

    if str(request.method) == 'POST':
        if form.is_valid():
            form.save()
            form = FormImportacaoVC()
            obj = Csv.objects.get()

            with open(obj.file_name.path, 'r') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')
                reader.__next__()
                data = []
                flag = 0

                for linha in reader:
                    print(f'TESTE {linha[0]}, e {linha[9]}')
                    if not (linha[9]):
                        flag = 1
                        continue
                    else:
                        year = linha[0]
                        month = linha[1]
                        day = linha[2]
                        headline = linha[9]
                        text = linha[10]
                        media = linha[11]
                        media_credit = linha[12]
                        media_caption = linha[13]
                        #background = linha[14]

                        arqui = Noticia.objects.create(

                            year=year,
                            month=month,
                            day=day,
                            headline=headline,
                            text=text,
                            media=media,
                            media_credit=media_credit,
                            media_caption=media_caption,
                            #background=background
                        )

                    arqui.save()

                    if flag == 1:
                        csv_file = open(obj.file_name.path, 'w')

                        for i in data:
                            str1 = ','.join(i)
                            csv_file.write(str1+"\n")
                            print(f'str1: {str1}')
                        csv_file.close()

        else:
            messages.error(request, 'Erro ao enviar arquivo')

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
