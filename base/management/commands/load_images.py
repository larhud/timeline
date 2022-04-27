import os
import requests

from django.core.management.base import BaseCommand
from base.models import Noticia


class Command(BaseCommand):
    help = 'Remoção automatizada dos textos'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        img_path = os.path.join('/', base_dir, 'media', 'img')
        os.makedirs(img_path, exist_ok=True)
        tot_lidos = 0
        tot_scrap = 0
        for noticia in Noticia.objects.filter(url_valida=True, media__isnull=False):

            tot_lidos += 1
            filename = noticia.media.split('/')[-1]
            file_ext = filename.split('.')[-1].split('?')[0]
            if len(file_ext) > 4 or len(file_ext) == 0 or file_ext == 'img':
                file_ext = 'jpeg'
            filename = "%s/%d.%s" % (img_path, noticia.id, file_ext)
            try:
                headers = {'user-agent':
                           'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}
                response = requests.get(noticia.media, headers=headers, timeout=10)
                if response.status_code == 200:
                    with open(filename, 'wb') as file:
                        file.write(response.content)
                        tot_scrap += 1
                else:
                    filename = None
            except Exception as e:
                filename = None

            if filename:
                noticia.imagem = 'media/img/'+filename.split('/')[-1]
                noticia.save()
            else:
                if not noticia.imagem:
                    print(f'Imagem não carregada: {noticia.id}')

        print(f'Total de registros lidos: {tot_lidos}')
        print(f'Total de registros capturados: {tot_scrap}')
