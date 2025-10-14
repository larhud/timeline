import mimetypes
import logging
import re
import os

from http import HTTPStatus
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.conf import settings


logger = logging.getLogger(__name__)


def noticia_imagem_path():
    base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]
    base_dir = '/'.join(base_dir)
    img_path = os.path.join('/', base_dir, 'media', 'img')
    os.makedirs(img_path, exist_ok=True)
    return img_path


# remove all script and style elements from HTML
# input: html string
# output: soup object
def extract_scripts_and_styles(html):
    soup = BeautifulSoup(html, features="html.parser")
    for script in soup(["script", "style", "noscript"]):
        script.extract()
    return soup


# obtem o HTML a partir da URL e retorna um soup object
# se use_cache=False, a rotina irá buscar da URL original mesmo que já exista um cache
def load_html(url, file_id, use_cache=False, timeout=10):
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
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code == HTTPStatus.OK:
            soup = extract_scripts_and_styles(response.content)
            if soup and not use_cache:
                with open(f"{html_path}/{file_id}.html", 'w') as file:
                    file.write(str(soup))
            return soup
        else:
            return
    except Exception as e:
        return


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




class BaseDownload:
    """Classe base para download de um arquivo e retorno do caminho relativo"""

    def __init__(self, url, file_path, id_noticia):
        self.url = url
        self.file_path = file_path
        self.id_noticia = id_noticia
        self.chunk_size = 32768

    def download(self):
        """
        Função abstrata. Responsável por:
        1. Fazer a requisição HTTP.
        2. Determinar a extensão.
        3. Chamar e retornar o resultado de _download_and_stream_to_disk.
        """
        raise NotImplementedError()

    def __call__(self):
        return self.download()

    def get_filename(self):
        return self.url.split('/')[-1].split('?')[0]

    def _download_and_stream_to_disk(self, response, new_file_name):
        """
        Grava o conteúdo da resposta HTTP no disco em chunks.

        :param response: Objeto requests.Response com stream=True.
        :param new_file_name: Nome final do arquivo (ex: 123.jpg).
        :return: Caminho relativo do arquivo salvo.
        """
        full_path = os.path.join(self.file_path, new_file_name)

        try:
            with open(full_path, "wb") as f:
                for chunk in response.iter_content(self.chunk_size):
                    if chunk:
                        f.write(chunk)
            # Retorna o caminho relativo
            return os.path.join(settings.MEDIA_URL, 'img', new_file_name)

        except Exception as e:
            logger.error(f'Erro ao escrever arquivo no disco: {full_path}. Erro: {e}', exc_info=True)
            return None


class RegularImageDownload(BaseDownload):
    """Baixa a imagem de uma url regular"""

    def download(self):
        try:
            headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}
            response = requests.get(self.url, headers=headers, timeout=10)

            if response.status_code != HTTPStatus.OK:
                return None

            server_filename = self.get_filename()

            file_ext = server_filename.split('.')[-1]

            if len(file_ext) > 4 or len(file_ext) == 0 or file_ext == 'img':
                file_ext = 'jpeg'

            new_file_name = '%d.%s' % (self.id_noticia, file_ext)

            return self._download_and_stream_to_disk(response, new_file_name)
        except Exception as e:
            logger.error(f'Erro no download da url {self.url}: {e}', exc_info=True)
            return None


class GoogleDriveDownload(BaseDownload):
    """
    Baixa um arquivo do Google Drive usando o ID do arquivo e o truque da URL de download direto.
    """
    # URL de Download Direto
    DOWNLOAD_URL = "https://drive.google.com/uc?export=download"

    def get_filename(self):
        """
        Extrai o ID do arquivo de diferentes formatos de URL do Google Drive/Colab.
        """
        url = self.url
        # Regex que busca por padrões comuns:
        # 1. /d/ID_DO_ARQUIVO/view ou /d/ID_DO_ARQUIVO/edit, etc.
        # 2. /drive/ID_DO_ARQUIVO?
        # 3. id=ID_DO_ARQUIVO (Links de download)

        # Regex (O ID do Google Drive consiste em caracteres alfanuméricos, hífens e underscores)
        match = re.search(r'file/d/([\w-]+)|/drive/([\w-]+)\?|id=([\w-]+)', url)

        if match:
            # O ID será o primeiro grupo capturado não nulo (1, 2 ou 3)
            # Ex: (None, '1pgfnyAxAWa2hnIeFPj8T91MGLhrYSPbb', None)
            file_id = next(filter(None, match.groups()), None)

            if file_id:
                return file_id

        logger.error(f'Não foi possível encontrar um ID de arquivo/pasta na URL do Drive: {url}')
        return None

    def download(self):
        try:
            # 1. Configuração da Sessão
            session = requests.Session()
            # 2. Faz a primeira requisição GET com o ID do arquivo
            file_id = self.get_filename()
            response = session.get(self.DOWNLOAD_URL, params={'id': file_id}, stream=True)
            # 3. Verifica se há um aviso de segurança/vírus (para arquivos grandes)
            # O Google Drive às vezes exibe um aviso para arquivos grandes, exigindo a confirmação 'confirm=...'
            token = self.get_confirm_token(response)

            if token:
                # Se houver token, faz uma nova requisição com a confirmação
                params = {'id': file_id, 'confirm': token}
                response = session.get(self.DOWNLOAD_URL, params=params, stream=True)

            if response.status_code != HTTPStatus.OK:
                return None
            # 4. Obtem a extensão do arquivo e monta no nome dele
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            raw_ext = mimetypes.guess_extension(content_type)
            # Remove o ".", caso exista. Retorna jpeg como fallback.
            raw_ext = raw_ext.split('.')[-1] or 'jpeg'
            new_file_name = '%s.%s' % (self.id_noticia, raw_ext)

            return self._download_and_stream_to_disk(response, new_file_name)
        except Exception as e:
            logger.error(f'Erro no download da url {self.url}: {e}', exc_info=True)
            return None

    @staticmethod
    def get_confirm_token(response):
        """
        Extrai o token de confirmação necessário para baixar arquivos grandes.
        """
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None


def save_image(url, full_path, id_noticia):
    """
    Executa a classe que salva a imagem indicada na URL no path indicado.
    A tipo da imagem é "calculado" e incluído ao path.
    """
    download_map = {
        'drive.google.com': GoogleDriveDownload,
    }

    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    downloader_class = download_map.get(domain, RegularImageDownload)

    return downloader_class(url, full_path, id_noticia)()
