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

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
    }

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

        parsed_url = urlparse(url)
        domain_full = parsed_url.netloc

        noticia = Noticia.objects.filter(url=url).first()
        canal = Canal.objects.filter(domain=domain_full).first() or Canal.objects.create(domain=domain_full)

        regras = CanalRegra.objects.filter(canal=canal, tipo_regra='C')
        if not regras.exists():
            print(f'Nenhuma regra encontrada para o canal: {canal.domain}')
            return

        html_content = self.load_html(url, canal.id, use_cache=True)
        if not html_content:
            print("Página sem conteúdo")
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        rows = []

        for regra in regras:
            tag, attr_value = eval(regra.regra)
            print(f"Processando regra: {tag}, {attr_value}")

            # Verificamos se ':' está presente em attr_value
            if ':' in attr_value:
                attr_name, attr_val = attr_value.split(':')
                # Aqui substituímos o nome do atributo incorreto pelo correto
                attr_name = "property"
                # E ajustamos o valor do atributo
                attr_val = f"rnews:{attr_val}"
                base_elements = soup.select(f"{tag}[{attr_name}='{attr_val}']")
            else:
                base_elements = soup.select(f"{tag}.{attr_value}")

            if not base_elements:
                print(
                    f"Nenhum elemento encontrado para a regra: {tag}, {attr_value}")  # Debug: Imprime se nenhum elemento foi encontrado
                continue

            for base_element in base_elements:
                elements = base_element.find_all(True)
                for element in elements:
                    texto = element.get_text(strip=True)
                    if texto:
                        print(f"Texto encontrado: {texto}")  # Debug: Imprime o texto encontrado
                        rows.append({'Id': None, 'Texto': texto})

        df = pd.DataFrame(rows)
        df['Id'] = df.index

        print("\nConteúdo do DataFrame:")
        print("----------------------")
        print(df)