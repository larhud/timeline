import os
import requests
from bs4 import BeautifulSoup
from django.conf import settings


# remove all script and style elements from HTML
# input: html string
# output: soup object
def extract_scripts_and_styles(html):
    soup = BeautifulSoup(html, features="html.parser")
    for script in soup(["script", "style", "noscript"]):
        script.extract()
    return soup


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


# Rotina salva a imagem indicada na URL no path indicado.
# A tipo da imagem é "calculado" e incluído ao path
def save_image(url, full_path, id_noticia):
    server_filename = url.split('/')[-1]
    file_ext = server_filename.split('.')[-1].split('?')[0]
    if len(file_ext) > 4 or len(file_ext) == 0 or file_ext == 'img':
        file_ext = 'jpeg'
    full_path += '/%d.%s' % (id_noticia, file_ext)
    try:
        headers = {'user-agent':
                       'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(full_path, 'wb') as file:
                file.write(response.content)
            relative_path = '/media/img/' + full_path.split('/')[-1]
        else:
            relative_path = None
    except Exception as e:
        relative_path = None
    return relative_path


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
        for line in soup.find_all("div", {"class": ["noticia", "entry-body",
                                                    "content-text", "content-noticia", "post-item-wrap"]}):
            link = line.find('img')
            if link:
                imagem = link['src']
                break

    if not imagem:
        for link in soup.find_all('img'):
            imagem = link['src']
            break

    return imagem
