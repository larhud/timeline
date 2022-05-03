import os
import re
import requests

from bs4 import BeautifulSoup

from django.conf import settings
from django.core.management.base import BaseCommand
from base.models import Noticia
from urllib.parse import urlparse


def get_url_base(url):
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)


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


# Busca a imagem mais relevante no objeto Soup
# Busca pelo og:image, twitter:image ou imagem dentro das tags de notícia
def scrap_best_image(soup):
    imagem = None
    tag = soup.find("meta", property="og:image")
    if tag:
        imagem = tag['content']
    else:
        tag = soup.find("meta", property="”twitter:image”")
        if tag:
            imagem = tag['content']

    if not imagem:
        for line in soup.find_all("div", {"class": ["noticia-img", ]}):
            link = line.find('img')
            if link:
                imagem = link['src']
                break

    if not imagem:
        for line in soup.find_all("div", {"class": [ "noticia", "entry-body",
                                                     "content-text", "content-noticia", "post-item-wrap" ]}):
            link = line.find('img')
            if link:
                imagem = link['src']
                break

    if not imagem:
        for link in soup.find_all('img'):
            imagem = link['src']
            break

    return imagem


def save_image(url, full_path):
    server_filename = url.split('/')[-1]
    file_ext = server_filename.split('.')[ -1 ].split('?')[ 0 ]
    if len(file_ext) > 4 or len(file_ext) == 0 or file_ext == 'img':
        file_ext = 'jpeg'
    full_path += '.' + file_ext
    try:
        headers = {'user-agent':
                       'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(full_path, 'wb') as file:
                file.write(response.content)
            relative_path = '/media/img/'+full_path.split('/')[-1]
        else:
            relative_path = None
    except Exception as e:
        relative_path = None
    return relative_path


# obtem o HTML retirado da URL e retorna um soup object
# se use_cache=False, a rotina irá buscar da URL original mesmo que já exista um cache
def load_html(url, file_id, use_cache=False):

    html_path = os.path.join(settings.MEDIA_ROOT, 'html')
    if use_cache:
        filename = f"{html_path}/{file_id}.html"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                html = f.read()
                return extract_scripts_and_styles(html)
        else:
            use_cache = False

    try:
        headers = {'user-agent':
                   'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = extract_scripts_and_styles(response.content)
            if soup and not use_cache:
                with open(f"{html_path}/{file_id}.html", 'w') as file:
                    file.write(str(soup))
            return soup
        else:
            return
    except Exception as e:
        return


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

