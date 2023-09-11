import os
import json
import pandas as pd

import chardet
import requests
import unicodedata
import urllib3
import html

from django.core.management.base import BaseCommand
from django.conf import settings
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urlsplit
from chardet import detect
from fuzzywuzzy import fuzz

from base.models import Canal, CanalRegra, Noticia


class Command(BaseCommand):
    help = 'Analisa as notícias já revisadas'

    # Desative o aviso InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    HEADERS = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'
    }

    EXCLUDED_TAGS = {'html', 'footer', 'em', 'section', 'header', 'body', 'style', 'nav', 'link', 'meta', 'img', 'icon', 'head', 'title', 'i', 'script', 'audio', 'source', 'noscript', 'button', 'submit', 'ul', 'li'}

    @staticmethod
    def get_encoding(filename, read_size=10000):
        """
                Detecta a codificação de um arquivo. Essencial para ler corretamente
                arquivos que podem ter diferentes codificações.
                """
        with open(filename, 'rb') as f:
            raw_data = f.read(read_size)
            encoding = detect(raw_data).get('encoding', 'utf-8')
            return encoding or 'utf-8'

    @staticmethod
    def extract_text(tag):
        """
                Verifica se uma determinada tag tem texto relevante. Útil para descartar
                tags que não adicionam informação significativa.
                """
        if tag.string and tag.string.strip() != "--":
            return True
        if isinstance(tag, Tag):
            for child in tag.descendants:
                if isinstance(child, NavigableString) and child.strip():
                    return True
        return False

    @staticmethod
    def extract_scripts_and_styles(html):
        """
                Limpa o HTML, removendo tags não desejadas como scripts, styles e noscripts.
                Isso torna o HTML mais manejável e focado no conteúdo.
                """
        soup = BeautifulSoup(html, features="html.parser")
        for script in soup(["script", "style", "noscript"]):
            script.extract()
        return soup

    def load_html(self, url, file_id, use_cache=False):
        """
        Carrega o HTML de uma URL. Se o caching estiver habilitado, a função
        primeiro tenta recuperar o conteúdo de um arquivo local em vez de
        fazer uma nova requisição HTTP.
        """

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
        """
                Função auxiliar para adicionar argumentos CLI personalizados a este comando Django.
                Permite que os usuários especifiquem qual notícia processar ao executar o comando.
                """
        parser.add_argument('--noticia_id', type=int, help='ID da notícia a ser processada.')

    def normalize_text(self, text):
        """
        Limpa e normaliza o texto. Útil para garantir consistência ao comparar
        strings ou ao armazenar informação.
        """
        # Removendo caracteres problemáticos ou normalizando-os
        normalized_text = text.replace('“', '"').replace('”', '"').strip()
        normalized_text = normalized_text.replace("&nbsp;", " ").strip()  # Convertendo &nbsp; para espaço
        return normalized_text

    def normalize_and_clean_text(self, text):
        # Funções de limpeza e normalização combinadas aqui
        cleaned_text = text.replace('\n', ' ').replace('\r', '').strip()
        cleaned_text = cleaned_text.replace('“', '"').replace('”', '"').replace("&nbsp;", " ").strip()

        # Decodifica entidades HTML
        cleaned_text = html.unescape(cleaned_text)

        # Corrigindo codificação
        try:
            byte_str = cleaned_text.encode("iso-8859-1")
            cleaned_text = byte_str.decode("utf-8")
        except:
            pass

        # Não remover acentos, apenas normalizar para a forma composta.
        normalized_text = unicodedata.normalize('NFC', cleaned_text)

        return normalized_text

    def fix_encoding(self, text):
        # Correções específicas para os caracteres
        corrections = {
            "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
            "Ã£": "ã", "Ãµ": "õ",
            "Ã¢": "â", "Ãª": "ê", "Ã®": "î", "Ã´": "ô", "Ã»": "û",
            "Ã§": "ç",
            "â€\"": "–", "â€œ": "“", "â€": "”",
            "Ã„": "Ä", "Ã‹": "Ë", "Ã": "Ï", "Ã–": "Ö", "Ãœ": "Ü",
            "Ãƒ": "Ã", "Ã•": "Õ",
            "Ã‚": "Â", "ÃŠ": "Ê", "ÃŽ": "Î", "Ã”": "Ô", "Ã›": "Û",
            "Ã‡": "Ç",
            "Ã‰": "É", "Ã": "Í", "Ã“": "Ó", "Ãš": "Ú",
        }

        for original, corrected in corrections.items():
            text = text.replace(original, corrected)

        return text

    def find_parent_with_attributes(self, tag):
        """
        Procura pelo ancestral (pai, avô, etc.) mais próximo que tem um atributo 'class' ou 'id' ou 'property'.
        """
        attributes_order = ['class', 'id', 'property']

        # Verificar o próprio elemento antes de verificar os antepassados
        for attribute in attributes_order:
            if attribute in tag.attrs:
                return tag, attribute

        parent = tag.find_parent()
        while parent:
            for attribute in attributes_order:
                if attribute in parent.attrs:
                    return parent, attribute
            parent = parent.find_parent()
        return None, None

    def clean_text(self, text):
        """
                Função de utilidade simples que remove espaços extras de um texto.
                Garante que o texto seja consistente e fácil de comparar.
                """
        return " ".join(text.split())

    def handle(self, *args, **kwargs):
        """
        Função principal do comando. Processa notícias (baseado em um ID fornecido ou todas disponíveis),
        carrega o conteúdo HTML, analisa tags, compara texto das tags com o texto da notícia e
        cria ou atualiza regras associadas.
        """
        noticia_id = kwargs.get('noticia_id')

        if noticia_id:
            try:
                noticias = [Noticia.objects.get(id=noticia_id)]
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
            canal, _ = Canal.objects.get_or_create(domain=domain)

            html_content = self.load_html(noticia.url, noticia.id, use_cache=True)
            if not html_content:
                print("Página sem conteúdo")
                continue

            soup = BeautifulSoup(html_content, 'html.parser')

            # Iterando sobre todas as tags <a>, <strong>, <b>, <i> e <span> encontradas no documento HTML
            for a_tag in soup.find_all(['a', 'strong', 'b', 'i', 'span']):
                # Substituindo cada uma dessas tags pelo seu respectivo conteúdo de texto.
                a_tag.replace_with(a_tag.string if a_tag.string else "")

            df_noticia = pd.DataFrame(noticia.texto_completo.split('\n'), columns=['paragrafo'])
            df_noticia['paragrafo'] = df_noticia['paragrafo'].apply(lambda x: self.clean_text(self.normalize_text(x)))
            df_noticia['Situacao'] = 0
            df_noticia['TextoTag'] = "--"
            df_noticia = df_noticia[df_noticia['paragrafo'].str.strip() != ""]

            for tag in soup.find_all():
                if tag.name in self.EXCLUDED_TAGS:
                    continue

                tag_content = self.normalize_and_clean_text(tag.get_text())
                tag_content = self.fix_encoding(tag_content)

                if not tag_content:
                    continue

                parent_with_attributes, attribute = self.find_parent_with_attributes(tag)
                if attribute == 'class':
                    tag_class = " ".join(parent_with_attributes.attrs['class'])
                elif attribute == 'id':
                    tag_class = parent_with_attributes.attrs['id']
                elif attribute == 'property':
                    tag_class = parent_with_attributes.attrs['property']
                else:
                    tag_class = None

                tag_name = tag.name if parent_with_attributes is None else parent_with_attributes.name

                matched_rows = df_noticia[df_noticia['paragrafo'] == tag_content]
                if matched_rows.shape[0] > 0 and matched_rows['Situacao'].iloc[0] == 1:
                    tipo_regra = 'C'
                else:
                    tipo_regra = 'I'

                if matched_rows.shape[0] == 0:
                    for index, row in df_noticia.iterrows():
                        similarity = fuzz.partial_ratio(row['paragrafo'], tag_content)
                        if similarity > 79:
                            if index < len(df_noticia):
                                matched_rows = df_noticia.iloc[[index]]
                                print(f"Similaridade entre '{row['paragrafo']}' e '{tag_content}': {similarity}%")

                if matched_rows.shape[0] > 0:
                    df_noticia.loc[matched_rows.index, 'Situacao'] = 1
                    df_noticia.loc[matched_rows.index, 'TextoTag'] = tag_content
                    df_noticia.loc[
                        matched_rows.index, 'TagClass'] = f"Tag: {tag_name}  {attribute.capitalize()}: {tag_class}"

                df_noticia.reset_index(drop=True, inplace=True)
                CanalRegra.objects.get_or_create(canal=canal, tipo_regra=tipo_regra,
                                                 regra=json.dumps((tag_name, tag_class)))

            # Cria regras para todas as tags e classes da coluna 'TagClass' com Situacao = 1
            df_filtered = df_noticia[df_noticia['Situacao'] == 1]
            for _, row in df_filtered.iterrows():
                tag_name, tag_class = None, None
                tag_and_class_info = row['TagClass'].split('  ')
                if len(tag_and_class_info) == 2:
                    tag_info, class_info = tag_and_class_info
                    tag_name = tag_info.split(': ')[1].strip()
                    tag_class = class_info.split(': ')[1].strip()

                # Aqui garantimos que estamos criando apenas as regras baseadas no DataFrame
                CanalRegra.objects.get_or_create(canal=canal, tipo_regra='C', regra=json.dumps((tag_name, tag_class)))

            print(df_noticia)
