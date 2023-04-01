import os
import re

from django.core.management.base import BaseCommand
from base import save_image, scrap_best_image, load_html
from base.models import Noticia
from urllib.parse import urlparse


def get_url_base(url):
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)


def extract_text(soup):
    texto = ""
    for line in soup.find_all("div", {"class": ["noticia", "entry-body", "articleBody",
                                                "content-text", "post-item-wrap"]}):
        if line.text:
            texto += line.text + '\n'

    for line in soup.find_all("section", {"class": ["internalContent"]}):
        if line.text:
            texto += line.text

    if not texto:
        for line in soup.find_all("div", {"class": ["text", "text   "]}):
            if line.text:
                texto += line.text + '\n'

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
    help = 'Carga automatizada dos textos'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=str, help='Id da Notícia')
        parser.add_argument('-m', '--imagem', help='Imagem mais relevante', action='store_true')

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        id = options['id']
        html_path = os.path.join('/', base_dir, 'media', 'html')
        img_path = os.path.join('/', base_dir, 'media', 'img')
        tot_lidos = 0
        tot_imagens = 0
        tot_gravados = 0
        for noticia in Noticia.objects.filter(id=id):
            tot_lidos += 1
            soup = load_html(html_path, noticia.id, use_cache=True)
            if soup:
                if options['imagem']:
                    imagem_url = scrap_best_image(soup)
                    filename = "%s/%d" % (img_path, noticia.id)
                    imagem = save_image(imagem_url, filename)
                    if imagem:
                        noticia.imagem = imagem
                        noticia.save()
                        tot_imagens += 1
                else:
                    texto = extract_text(soup)
                    if texto:
                        noticia.texto_completo = texto
                        noticia.atualizado = True
                        noticia.save()
                        tot_gravados += 1
            else:
                print(f'URL não encontrada: {noticia.url}')

        print(f'Total de registros lidos: {tot_lidos}')
        print(f'Total de imagens gravadas: {tot_imagens}')
        print(f'Total de textos extraídos: {tot_gravados}')

