import os
import re

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from base.models import Noticia


# remove all script and style elements from HTML
# input: html string
# output: soup object
def extract_scripts_and_styles(html):
    soup = BeautifulSoup(html, features="html.parser")
    for script in soup(["script", "style", "noscript"]):
        script.extract()
    return soup


def extract_text(soup):
    texto = ""
    for line in soup.find_all("div", {"class": [ "content-text", "text", "text   ", "post-item-wrap"]}):
        if line.text:
            texto += line.text + '\n'

    for line in soup.find_all("section", {"class": ["internalContent"]}):
        if line.text:
            texto += line.text

    if not texto:
        for article in soup.find_all("article"):
            for lines in article.find_all("div"):
                line = re.sub("\s+", " ", lines.text).strip()
                if line:
                    texto += line + '\n'

    if not texto:
        texto = soup.get_text()

    lines = (line.strip() for line in texto.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    texto = '\n'.join(chunk for chunk in chunks if chunk)

    return texto


class Command(BaseCommand):
    help = 'Remoção automatizada dos textos'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=str, help='Id da Notícia')

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        id = options['id']
        html_path = os.path.join('/', base_dir, 'media', 'html')
        for noticia in Noticia.objects.filter(atualizado=False, revisado=False, id=id):
            if os.path.exists("%s/%d.html" % (html_path, noticia.id)):
                with open(f"{html_path}/{id}.html", 'r') as f:
                    html = f.read()
            else:
                print('HTML não encontrado')

            soup = BeautifulSoup(html, features="html.parser")
            cleaned = id is not None
            for script in soup([ "script", "style", "noscript" ]):
                script.extract()  # rip it out all scripts and styles
                cleaned = True

            if cleaned:
                texto = extract_text(soup)
                if texto:
                    noticia.texto_completo = texto
                    noticia.atualizado = True
                    noticia.save()
