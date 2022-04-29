import os
import requests

import hashlib

from django.core.management.base import BaseCommand
from base.models import Noticia


class Command(BaseCommand):
    help = 'Verifica se as URLs são válidas'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=str, help='Id da Notícia')

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        id = options['id']
        html_path = os.path.join('/', base_dir, 'media', 'html')
        pdf_path = os.path.join('/', base_dir, 'media', 'pdf')
        if id:
            queryset = Noticia.objects.filter(id=id)
        else:
            queryset = Noticia.objects.all()

        for noticia in queryset:
            try:
                real_hash = hashlib.sha256(noticia.url.encode('utf-8')).hexdigest()
                if real_hash != noticia.url_hash:
                    dset = Noticia.objects.filter(url_hash=real_hash).exclude(id=noticia.id)
                    if dset.count() != 0:
                        print(f'URL Duplicada {noticia.id_externo} {noticia.url}')

                '''
                response = requests.head(noticia.url, timeout=5)
                if response.status_code != 200:
                    if response.history:
                        print("Request was redirected")
                        for resp in response.history:
                            print(resp.status_code, resp.url)
                        print("Final destination:")
                        print(response.status_code, response.url)
                    else:
                        if noticia.url_valida:
                            print(f'URL não validada com ID: {noticia.id}')
                '''
            except Exception as e:
                print(e.__str__())
