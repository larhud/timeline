import os
import json

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

    DOMAIN_TAGS = {
        "g1.globo.com": {
            "accepted_tags": {
                'div': ["row content-head non-featured ", "row content-head non-featured2 ",
                        "content-publication-data"],
                'h1': ["content-head__title", "content-head__subtitle"],
                'p': ["content-media__description", "content-text__container"],
            },
            "ignored_tags": {
                'script': ["text/javascript SETTINGS", "text/javascript", "application/json", "text/javascript CDA_AAS",
                           None],
                'div': ["content__share-bar", "mc-column content-entenda-o-caso"]
            }
        },
        "agenciabrasil.ebc.com.br": {
            "accepted_tags": {
                'div': ["row content-head non-featured ", "row content-head non-featured2",
                        "content-publication-data", "post-item-wrap"],
                'h1': ["content-head__title", "content-head__subtitle"],
                'h2': [
                    "col-10 offset-1 animated fadeInDown dealy-750 display-6 display-md-4 display-lg-5 font-weight-bold alt-font text-center my-1"],
                'h3': [
                    "col-10 offset-1 animated fadeInDown dealy-900 display-8 display-md-8 alt-font font-italic my-1 text-center"],
                'span': ["badge badge-pill badge-warning"],
                'p': ["content-media__description", "content-text__container",
                      "alt-font font-italic my-2 small text-info"],
            },
            "ignored_tags": {
                'script': ["text/javascript SETTINGS", "text/javascript", "application/json", "text/javascript CDA_AAS",
                           None],
                'div': ["col-xl-7 offset-xl-1 col-lg-8 offset-lg-0 col-md-10 offset-md-1 mb-3", "__m",
                        "eouv-manifestacoes d-print-none",
                        "col-xl-7 offset-xl-1 col-lg-8 offset-lg-0 col-md-10 offset-md-1 mb-3"],
                'ul': ["divider social-icons si-border round si-colored-bg-on-hover my-3"],
                'li': ["social-icons-item social-whatsapp", "social-icons-item social-facebook",
                       "social-icons-item social-twitter", "social-icons-item social-linkedin"],
                'h4': [
                    "col-10 offset-1 animated fadeInDown dealy-1100 alt-font font-italic my-2 small text-info text-center",
                    "alt-font font-italic small text-info text-left"],
                'nav': ["navbar"],
                'img': ["access-button"],
                'span': ["sr-only"]
            }
        },
        "agenciaamazonas.am.gov.br": {
            "accepted_tags": {
                'div': ["col-md-8 col-12 mx-auto"],
                'h1': ["title-post-photo"],
                'span': ["post-date internal d-block"],
            },
            "ignored_tags": {
                'script': ["text/javascript SETTINGS", "text/javascript", "application/json", "text/javascript CDA_AAS",
                           None],
                'div': ["row row-social", "container-fluid", "row mt-4 mt-md-0"],
                'ul': ["social mt-md-5", "social"],
                'li': [" facebook menu-item menu-item-type-custom menu-item-object-custom menu-item-1302 nav-item",
                       " youtube menu-item menu-item-type-custom menu-item-object-custom menu-item-1304 nav-item",
                       " instagram menu-item menu-item-type-custom menu-item-object-custom menu-item-1305 nav-item",
                       " twitter menu-item menu-item-type-custom menu-item-object-custom menu-item-1306 nav-item"],
                'a': ["nav-link"]
            }
        },
        "www.correiobraziliense.com.br": {
            "accepted_tags": {
                'div': ["materia-title", "date"],
                'p': ["texto"]
            },
            "ignored_tags": {
                'script': ["text/javascript SETTINGS", "text/javascript", "application/json", "text/javascript CDA_AAS",
                           None],
                'div': ["socialBar"]
            }
        },
        "www.finep.gov.br": {
            "accepted_tags": {
                'div': ["item-pagerevistas", "articleBody"],
                'p': ["texto"]
            },
            "ignored_tags": {
                'script': ["text/javascript SETTINGS", "text/javascript", "application/json", "text/javascript CDA_AAS",
                           None],
                'div': ["topo-interior-2", "menu-mobile","icon-share"]
            }
        },
        "www.ans.gov.br": {
            "accepted_tags": {
                'div': ["page-header", "col-xs-12 col-sm-8 col-md-9"]
            },
            "ignored_tags": {
                'script': ["text/javascript SETTINGS", "text/javascript", "application/json", "text/javascript CDA_AAS",
                           None],
                'div': ["rodape-mapa-site-ans", "boxcinza-ans"],
                'p': ["muted"]

            }
        },
        # outros domínios...
    }

    @staticmethod
    def get_encoding(filename, read_size=10000):
        with open(filename, 'rb') as f:
            raw_data = f.read(read_size)
            encoding = detect(raw_data).get('encoding', 'utf-8')

            if encoding:
                return encoding if encoding.lower() != 'utf-8' else 'utf-8'
            else:
                return 'utf-8'

    @staticmethod
    def extract_text(tag):
        if tag.string and tag.string.strip() != "--":
            return True
        if isinstance(tag, Tag):
            for child in tag.descendants:
                if isinstance(child, NavigableString) and child.strip():
                    return True
        return False

    def load_html(self, url, file_id, use_cache=False):
        html_path = os.path.join(settings.MEDIA_ROOT, 'html')
        os.makedirs(html_path, exist_ok=True)
        filename = f"{html_path}/{file_id}.html"

        if use_cache and os.path.exists(filename):
            with open(filename, 'rb') as f:  # Note o modo 'rb' aqui
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding']
                return raw_data.decode(encoding or 'utf-8', errors='replace')

        try:
            response = requests.get(url, headers=self.HEADERS, timeout=60, verify=False)
            response.raise_for_status()
            if response.status_code == 200:
                html = response.content

                try:
                    with open(filename, 'wb') as f:
                        f.write(html)
                except Exception as e:
                    print(f"Erro ao escrever no arquivo: {e}")
                return html
        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer a requisição: {e}")
        except Exception as e:
            print(f"Erro desconhecido: {e}")

        return None

    def add_arguments(self, parser):
        parser.add_argument('--noticia_id', type=int, help='ID da notícia a ser processada.')

    def handle(self, *args, **kwargs):
        noticia_id = kwargs.get('noticia_id')
        try:
            noticias = Noticia.objects.all() if noticia_id is None else [Noticia.objects.get(id=noticia_id)]
        except Noticia.DoesNotExist:
            print(f"Notícia com ID {noticia_id} não encontrada.")
            return

        for noticia in noticias:
            print(f"Processando notícia com ID: {noticia.id}")
            url = noticia.url
            domain = urlsplit(url).netloc
            canal, _ = Canal.objects.get_or_create(domain=domain)
            tags_data = self.DOMAIN_TAGS.get(domain, {})
            accepted_tags = tags_data.get("accepted_tags", {})
            ignored_tags = tags_data.get("ignored_tags", {})
            html_content = self.load_html(url, noticia.id, use_cache=True)

            if not html_content or html_content == "":
                print("Página sem conteúdo ")
                continue  # skip if there's no HTML content

            soup = BeautifulSoup(html_content, 'html.parser')
            for tag in soup.find_all():
                attrs_class = " ".join(tag.attrs.get('class', [])) or None
                if self.extract_text(tag):
                    tipo_regra = None
                    if tag.name in ignored_tags and (
                            not ignored_tags[tag.name] or attrs_class in ignored_tags[tag.name]):
                        tipo_regra = 'I'
                    elif tag.name in accepted_tags and (
                            not accepted_tags[tag.name] or attrs_class in accepted_tags[tag.name]):
                        tipo_regra = 'C'
                        print(f"Conteúdo da tag aceita -> '{tag.get_text()}'", f"-- Nome da Tag -> '{tag.name}'",
                              f"-- Nome da Class -> '{attrs_class}'")
                    if tipo_regra:
                        CanalRegra.objects.get_or_create(
                            canal=canal,
                            tipo_regra=tipo_regra,
                            regra=json.dumps((tag.name, attrs_class))
                        )
