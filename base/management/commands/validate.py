import os
import requests

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from base.models import Noticia


class Command(BaseCommand):
    help = 'Verifica se as URLs são válidas'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        html_path = os.path.join('/', base_dir, 'media', 'html')
        pdf_path = os.path.join('/', base_dir, 'media', 'pdf')
        for noticia in Noticia.objects.filter(url_valida=False):
            try:
                response = requests.head(noticia.url)
                if response.status_code == 200:
                    noticia.url_valida = True
                    noticia.save()
                else:
                    if response.history:
                        print("Request was redirected")
                        for resp in response.history:
                            print(resp.status_code, resp.url)
                        print("Final destination:")
                        print(response.status_code, response.url)
            except Exception as e:
                print(e.__str__())
