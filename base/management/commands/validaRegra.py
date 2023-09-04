from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
from base.models import Canal, CanalRegra, Noticia
from django.conf import settings

import pandas as pd
import os
import chardet
import requests


class Command(BaseCommand):
    help = 'Valida regras para um canal específico'

    def add_arguments(self, parser):
        parser.add_argument('--noticia_id', type=int, help='ID da Notícia (opcional)')

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
        noticia_id = options.get('noticia_id')

        if noticia_id:
            if not Noticia.objects.filter(id=noticia_id).exists():
                print(f'Notícia com ID {noticia_id} não encontrada.')
                return
            noticias = [Noticia.objects.get(id=noticia_id)]
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
            try:
                canal = Canal.objects.get(domain=domain)
            except Canal.DoesNotExist:
                print(f'Canal com domínio {domain} não encontrado. Por favor, adicione-o ao banco de dados.')
                continue

            regras = CanalRegra.objects.filter(canal=canal, tipo_regra='C')
            if not regras.exists():
                print(f'Nenhuma regra encontrada para o canal: {canal.nome}')
                continue

            # Carregando o HTML da notícia
            html_content = self.load_html(noticia.url, noticia.id, use_cache=True)
            if not html_content:
                print("Página sem conteúdo")
                continue

            soup = BeautifulSoup(html_content, 'html.parser')

            # Criando um DataFrame vazio
            df = pd.DataFrame(columns=['Id', 'Texto'])

            for regra in regras:
                tag, class_name = eval(regra.regra)
                selector = f"{tag}.{class_name}"
                elements = soup.select(selector)

                # Criando uma lista temporária para armazenar as linhas
                rows = [{'Texto': element.get_text(strip=True)} for element in elements]

                # Convertendo a lista temporária em um DataFrame e concatenando com o DataFrame original
                df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

            df['Id'] = df.index

            # Imprimir o conteúdo do DataFrame
            print("\nConteúdo do DataFrame:")
            print("-----------------------")
            print(df.to_string(index=False))
