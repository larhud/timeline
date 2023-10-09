import os
import json
import pandas as pd

import chardet
import requests
import urllib3

from django.core.management.base import BaseCommand
from django.conf import settings
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urlsplit
from chardet import detect

from base.models import Canal, CanalRegra, Noticia


class Command(BaseCommand):
    help = 'Analisa as notícias já revisadas'

    # Desative o aviso InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    HEADERS = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'
    }

    EXCLUDED_TAGS = {'nav', 'link', 'meta', 'img', 'icon', 'head', 'title', 'i', 'script', 'audio', 'source', 'noscript', 'button', 'submit', 'ul', 'li'}

    @staticmethod
    def get_encoding(filename, read_size=10000):
        with open(filename, 'rb') as f:
            raw_data = f.read(read_size)
            encoding = detect(raw_data).get('encoding', 'utf-8')
            return encoding or 'utf-8'

    @staticmethod
    def extract_text(tag):
        if tag.string and tag.string.strip() != "--":
            return True
        if isinstance(tag, Tag):
            for child in tag.descendants:
                if isinstance(child, NavigableString) and child.strip():
                    return True
        return False

    @staticmethod
    def extract_scripts_and_styles(html):
        soup = BeautifulSoup(html, features="html.parser")
        for script in soup(["script", "style", "noscript"]):
            script.extract()
        return soup

    def load_html(self, url, file_id, use_cache=False):
        """Carrega o HTML de uma URL"""

        html_path = os.path.join(settings.MEDIA_ROOT, 'html')
        os.makedirs(html_path, exist_ok=True)
        filename = f"{html_path}/{file_id}.html"

        # Se use_cache estiver ativo, tentar carregar o HTML do arquivo de cache.
        if use_cache and os.path.exists(filename):
            with open(filename, 'rb') as f:  # Note o modo 'rb' aqui
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding']
                return raw_data.decode(encoding or 'utf-8', errors='replace')
        else:
            # Se não estiver no cache ou use_cache estiver desativado, faça o download do HTML.
            try:
                response = requests.get(url, headers=self.HEADERS, timeout=10, verify=False)

                detected_encoding = chardet.detect(response.content)['encoding']

                # Tente decodificar com a codificação detectada
                try:
                    html_content = response.content.decode(detected_encoding)
                except UnicodeDecodeError:
                    # Se houver um erro com a codificação detectada, tenta utf-8
                    try:
                        html_content = response.content.decode('utf-8')
                    except UnicodeDecodeError:
                        # Se ainda houver um erro, tenta iso-8859-1
                        html_content = response.content.decode('iso-8859-1', errors='replace')

                # Se use_cache estiver ativo, salve o HTML em um arquivo de cache.
                if use_cache:
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    with open(filename, 'w', encoding='utf-8') as cache_file:
                        cache_file.write(html_content)

            except requests.RequestException as e:
                print(f"Erro ao obter HTML da URL {url}. Erro: {str(e)}")
                return None

        # Agora, vamos extrair e remover os scripts, styles, e noscript do HTML
        soup = self.extract_scripts_and_styles(html_content)
        return str(soup)  # Converta o objeto soup de volta para string antes de retornar

    def add_arguments(self, parser):
        parser.add_argument('--noticia_id', type=int, help='ID da notícia a ser processada.')

    def normalize_text(self, text):
        """Função para normalizar o texto."""
        # Removendo caracteres problemáticos ou normalizando-os
        normalized_text = text.replace('“', '"').replace('”', '"').strip()
        return normalized_text

    def find_parent_with_class(self, tag):
        """Procura a tag pai mais próxima com o atributo class."""
        parent = tag.find_parent()
        while parent:
            if 'class' in parent.attrs:
                return parent
            parent = parent.find_parent()
        return None

    def handle(self, *args, **kwargs):
        noticia_id = kwargs.get('noticia_id')

        if noticia_id:
            try:
                noticias = [Noticia.objects.get(id=noticia_id)]  # Assumindo que Noticia é um modelo
            except Noticia.DoesNotExist:
                print(f"Notícia com ID {noticia_id} não encontrada.")
                return
        else:
            count_noticias = Noticia.objects.count()
            if count_noticias > 100:
                confirm = input(f"Você está prestes a processar {count_noticias} notícias. Continuar? (y/n) ")
                if confirm.lower() != 'y':
                    print("Processamento cancelado.")
                    return
            noticias = Noticia.objects.all()

        for noticia in noticias:
            print(f"Processando notícia com ID: {noticia.id}")
            domain = urlsplit(noticia.url).netloc
            canal, _ = Canal.objects.get_or_create(domain=domain)  # Assumindo que Canal é um modelo

            html_content = self.load_html(noticia.url, noticia.id, use_cache=True)
            if not html_content:
                print("Página sem conteúdo")
                continue

            soup = BeautifulSoup(html_content, 'html.parser')

            # Removendo tags <a></a> mas mantendo o texto
            for a_tag in soup.find_all('a'):
                a_tag.replace_with(a_tag.string if a_tag.string else "")

            df_noticia = pd.DataFrame(noticia.texto_completo.split('\n'), columns=['paragrafo'])
            df_noticia['paragrafo'] = df_noticia['paragrafo'].apply(self.normalize_text)
            df_noticia['Situacao'] = 0
            df_noticia['TextoTag'] = "--"
            df_noticia = df_noticia[df_noticia['paragrafo'].str.strip() != ""]

            previous_tag_name = None
            previous_class = None

            for tag in soup.find_all():
                if tag.name in self.EXCLUDED_TAGS:
                    continue

                tag_content = self.normalize_text(tag.get_text(strip=True))
                if not tag_content:
                    continue

                if tag.name in ['p', 'span'] and ('class' not in tag.attrs or not tag.attrs['class']):
                    parent_with_class = self.find_parent_with_class(tag)
                    tag_class = " ".join(parent_with_class.attrs['class']) if parent_with_class else previous_class
                    tag_name = tag.name if parent_with_class is None else parent_with_class.name
                else:
                    tag_class = " ".join(tag.attrs.get('class', [])) or None
                    tag_name = tag.name
                    previous_class = tag_class

                matched_rows = df_noticia[df_noticia['paragrafo'] == tag_content]

                if matched_rows.shape[0] > 0:
                    tipo_regra = 'C'
                    df_noticia.loc[matched_rows.index, 'Situacao'] = 1
                    df_noticia.loc[matched_rows.index, 'TextoTag'] = tag_content
                    df_noticia.loc[matched_rows.index, 'TagClass'] = f"Tag: {tag_name}  Class: {tag_class}"
                else:
                    tipo_regra = 'I'
                    df_noticia.loc[matched_rows.index, 'TextoTag'] = tag_content
                    print(f"Conteúdo da tag aceita -> '{tag_content}'", f"-- Nome da Tag -> '{tag_name}'",
                          f"-- Nome da Class -> '{tag_class}'", f"-- Tipo Regra -> '{tipo_regra}'")

                CanalRegra.objects.get_or_create(canal=canal, tipo_regra=tipo_regra,
                                                 regra=json.dumps((tag.name, tag_class)))

            print(df_noticia)
