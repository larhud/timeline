from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from base.models import Canal, CanalRegra, Noticia
import requests
import json


class Command(BaseCommand):
    help = 'Analisa as notícias já revisadas'

    def handle(self, *args, **kwargs):
        # buscar a notícia com o id específico
        try:
            noticia = Noticia.objects.get(id=196)
            print(f"Processando notícia com ID: {noticia.id}")  # Exibe o ID da notícia que está sendo processada
        except Noticia.DoesNotExist:
            print("Notícia com ID 196 não encontrada.")
            return

        url = noticia.url
        texto_revisado = noticia.texto_completo

        # obter o domínio do site
        domain = urlparse(url).netloc
        print(f"Domínio da notícia: {domain}")  # Exibe o domínio da notícia

        # criar ou buscar o Canal
        canal, created = Canal.objects.get_or_create(domain=domain)
        print(
            f"Canal '{canal.domain}' {'criado' if created else 'já existe'}")  # Exibe se o canal foi criado ou já existia

        # fazer o request para a url e obter o conteúdo
        print("Fazendo request para a URL da notícia...")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # encontrar em quais tags o texto da notícia aparece
        print("Buscando tags no conteúdo da notícia...")
        for tag in soup.find_all():
            if tag.string and tag.string.strip():
                # ignore tags sem texto ou com apenas espaço em branco
                regra = {"tag": tag.name, "attrs": tag.attrs}
                regra_str = json.dumps(regra)  # regra como uma string para a comparação

                # Determina o tipo da regra baseado na presença do texto da tag no texto revisado
                tipo_regra = 'C' if tag.string.strip() in texto_revisado else 'I'

                # Obter ou criar a regra para o canal, evitando duplicações
                canal_regra, created = CanalRegra.objects.get_or_create(canal=canal, tipo_regra=tipo_regra,
                                                                        regra=regra_str)
                print(
                    f"Regra '{canal_regra.regra}' {'criada' if created else 'já existe'} para o canal '{canal.domain}'")  # Exibe se a regra foi criada ou já existia
