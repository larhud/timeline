import os
import requests

from django.core.management.base import BaseCommand
from base.models import Noticia
from .get_text import save_image


class Command(BaseCommand):
    help = 'Import as imagens em cache'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        img_path = os.path.join('/', base_dir, 'media', 'img')
        os.makedirs(img_path, exist_ok=True)
        tot_lidos = 0
        tot_scrap = 0
        for noticia in Noticia.objects.filter(url_valida=True, media__isnull=False, origem=2):
            tot_lidos += 1
            filename = "%s/%d" % (img_path, noticia.id)
            file_path = save_image(noticia.media, img_path)
            if file_path:
                tot_scrap += 1
                noticia.imagem = file_path
                noticia.save()
            else:
                print(f'Imagem não carregada: {noticia.id}')

        print(f'Total de registros lidos: {tot_lidos}')
        print(f'Total de registros capturados: {tot_scrap}')
