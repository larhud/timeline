from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urlsplit
from base.models import Canal, CanalRegra, Noticia
import requests
import json


class Command(BaseCommand):
    help = 'Analisa as notícias já revisadas'

    def handle(self, *args, **kwargs):
        try:
            noticia = Noticia.objects.get(id=24)
            print(f"Processando notícia com ID: {noticia.id}")
        except Noticia.DoesNotExist:
            print("Notícia com ID {noticia.id} não encontrada.")
            return

        url = noticia.url
        texto_revisado = noticia.texto_completo

        domain = "{0.netloc}".format(urlsplit(url))
        print(f"Domínio da notícia: {domain}")

        canal, created = Canal.objects.get_or_create(domain=domain)
        print(f"Canal '{canal.domain}' {'criado' if created else 'já existe'}")

        print("Fazendo request para a URL da notícia...")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        print("Buscando tags no conteúdo da notícia...")

        accepted_tags = set([
            ("p", "content-text__container"),
            ("p", "content-text__container theme-color-primary-first-letter"),
            ("h1", "content-head__title"),
            ("h1", "content-head__subtitle"),
            ("article", None),
            ("ul", "content-unordered-list"),
            ("h2", "col-10 offset-1 animated fadeInDown dealy-750 display-6 display-md-4 display-lg-5 font-weight-bold alt-font text-center my-1"),
            ("h3", "col-10 offset-1 animated fadeInDown dealy-750 display-6 display-md-4 display-lg-5 font-weight-bold alt-font text-center my-1"),
            ("h3", "col-10 offset-1 animated fadeInDown dealy-900 display-8 display-md-8 alt-font font-italic my-1 text-center"),
            ("h4", "col-10 offset-1 animated fadeInDown dealy-750 display-6 display-md-4 display-lg-5 font-weight-bold alt-font text-center my-1"),
            ("h4", "col-10 offset-1 animated fadeInDown dealy-1100 alt-font font-italic my-2 small text-info text-center"),
            ("div", "post-item-wrap"),
            ("div", "post-item alt-font"),
            ("p", "alt-font font-italic my-2 small text-info"),
            ("h2", "content-head__subtitle"),
            ("div", "content__signature"),
        ])

        ignored_tags = set([
            ("script", "text/javascript SETTINGS"),
            ("script", "text/javascript"),
            ("script", None),
            ("script", "application/json"),
            ("script", "text/javascript CDA_AAS"),
            ("div", "area-principal column"),
            ("div", "embed-responsive embed-responsive-16by9"),
            ("span", "menu-item-title"),
            ("ul", "divider social-icons si-border round si-colored-bg-on-hover my-3"),
            ("h4", "alt-font font-italic small text-info text-left"),
            ("div", "col-xl-7 offset-xl-1 col-lg-8 offset-lg-0 col-md-10 offset-md-1 mb-3"),
            ("img", "access-button"),
            ("div", "eouv-manifestacoes d-print-none"),
            ("div", "feature-box f-style-1 h-100 icon-grad border overflow-visible"),
            ("section", "ebc360 py-4 bg-light bgGray"),
            ("footer", "footer bg-dark text-white pt-4 mt-4"),
            ("a", "btn btn-grad px-3 py-1 text-white border-radius-3 zoom-on-hover-sm"),
            ("div", "sidemenu collapse horizontal shadow"),
            ("div", "block block-bloco-360"),
            ("div", "_li"),
            ("iframe"),
            ("p", "content-media__description mc-column "),
            ("div", "mc-column content-entenda-o-caso"),
            ("li", "content-entenda-o-caso__item"),
            ("p", "content-entenda-o-caso__text"),
            ("a","content-link gui-color-primary gui-color-hover"),
            ("h3","content-entenda-o-caso__title"),
            ("ul", "content-entenda-o-caso__list"),
        ])

        for tag in soup.find_all():
            attrs_class = tag.attrs.get('class', None)
            attrs_class = " ".join(attrs_class) if attrs_class else None
            regra = (tag.name, attrs_class)

            has_text = False
            if tag.string and tag.string.strip() != "--":
                has_text = True
            elif any(isinstance(child, NavigableString) and child.strip() for child in tag.descendants):
                has_text = True

            if has_text:
                if regra in ignored_tags:
                    tipo_regra = 'I'
                elif regra in accepted_tags:
                    tipo_regra = 'C'
                    if tag.name == "ul":
                        for li in tag.find_all("li"):
                            print(f"Conteúdo da tag li -> '{li.get_text()}'")
                    else:
                        print(f"Conteúdo da tag aceita -> '{tag.get_text()}'")
                else:
                    continue  # ignore a tag se não estiver em accepted_tags ou ignored_tags

                canal_regra, created = CanalRegra.objects.get_or_create(canal=canal, tipo_regra=tipo_regra,
                                                                        regra=json.dumps(regra))
