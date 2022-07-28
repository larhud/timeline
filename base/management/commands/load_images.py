import os
import requests

from django.core.management.base import BaseCommand
from base.models import Noticia
from timeline.settings import noticia_imagem_path
from base import save_image


class Command(BaseCommand):
    help = 'Import as imagens em cache'

    def handle(self, *args, **options):
        img_path = noticia_imagem_path()
        tot_lidos = 0
        tot_scrap = 0
        for noticia in Noticia.objects.filter(url_valida=True, media__isnull=False, imagem__isnull=True):
            tot_lidos += 1
            file_path = save_image(noticia.media, img_path, noticia.id)
            if file_path:
                tot_scrap += 1
                noticia.imagem = file_path
                noticia.save()
            else:
                print(f'Imagem ({noticia.id} não carregada: {noticia.media}')

        print(f'Total de registros lidos: {tot_lidos}')
        print(f'Total de registros capturados: {tot_scrap}')
