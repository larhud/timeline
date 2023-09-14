from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlparse
from base.models import Canal, CanalRegra, Noticia
from django.conf import settings

import pandas as pd
import os
import chardet
import requests


class Command(BaseCommand):
    help = 'Valida regras para um canal específico'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='URL da Notícia para processamento')

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

    def handle(self, *args, **options):
        url = options.get('url')
        if not url:
            print("URL não especificada.")
            return

        noticia = Noticia.objects.filter(url=url).first()
        parsed_url = urlparse(url)
        domain_full = parsed_url.netloc

        if not noticia:
            canal, created = Canal.objects.get_or_create(domain=domain_full)
            if created:
                print(f"Canal {canal.nome} criado com sucesso!")
        else:
            canal = Canal.objects.filter(domain=domain_full).first()

        regras = CanalRegra.objects.filter(canal=canal, tipo_regra='C')
        if not regras.exists():
            print(f'Nenhuma regra encontrada para o canal: {canal.domain}')
            return

        html_content = self.load_html(url, canal.id, use_cache=True)  # Usando canal.id em vez de noticia.id
        if not html_content:
            print("Página sem conteúdo")
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        rows = []

        for tag_name in ["a", "strong", "b", "i", "span"]:
            for tag in soup.find_all(tag_name):
                tag.replace_with(tag.get_text())

        for regra in regras:
            tag, attr_value = eval(regra.regra)
            if ':' in attr_value:
                elements = soup.select(f'{tag}[property="{attr_value}"]')
            else:
                elements = soup.select(f"{tag}.{attr_value}")

            for element in elements:
                if element.get_text(strip=True) and (
                        element.get('class') or element.get('id') or element.get('property')):
                    rows.append({
                        'Id': None,
                        'Texto': element.get_text(strip=True)
                    })

        df = pd.DataFrame(rows)
        df['Id'] = df.index

        print("\nConteúdo do DataFrame:")
        print("----------------------")
        print(df.to_string(index=False))