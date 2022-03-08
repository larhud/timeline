import os
import requests

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from base.models import Noticia


class Command(BaseCommand):
    help = 'Remoção automatizada dos textos'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=str, help='Id da Notícia')

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        id = options['id']
        html_path = os.path.join('/', base_dir, 'media', 'html')
        for noticia in Noticia.objects.filter(id=id):
            with open(f"{html_path}/{id}.html", 'r') as f:
                html = f.read()

            soup = BeautifulSoup(html, features="html.parser")
            texto = ""
            for line in soup.find_all("div", {"class": "content-text"}):
                texto += line + '\n'
            noticia.texto_completo = texto
            noticia.save()
