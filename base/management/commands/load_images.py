import os
import requests

from django.core.management.base import BaseCommand
from base.models import Noticia
from timeline.settings import noticia_imagem_path
from base import save_image, scrap_best_image, load_html


class Command(BaseCommand):
    help = 'Import as imagens em cache'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=int, help='Id da Notícia', default=0)

    def handle(self, *args, **options):
        img_path = noticia_imagem_path()
        tot_lidos = 0
        tot_scrap = 0
        if options['id'] == 0:
            dataset = Noticia.objects.filter(url_valida=True, media__isnull=False, imagem__isnull=True)
        else:
            dataset = Noticia.objects.filter(id=options['id'])
            if dataset.count() == 0:
                print('Noticia %d não encontrada' % options['id'])
            else:
                if not dataset[0].media:
                    base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
                    base_dir = '/'.join(base_dir)
                    html_path = os.path.join('/', base_dir, 'media', 'html')
                    soup = load_html(html_path, options['id'], use_cache=True)
                    imagem_url = scrap_best_image(soup)
                    print('Nenhuma imagem definida' % options['id'])

        for noticia in dataset:
            tot_lidos += 1
            file_path = save_image(noticia.media, img_path, noticia.id)
            if file_path:
                tot_scrap += 1
                noticia.imagem = file_path
                if noticia.notas:
                    noticia.notas = noticia.notas.replace('[Imagem não recuperada]', '')
                noticia.save()
            else:
                termos = noticia.assunto_set.all()
                if len(termos) > 0 and termos[0].termo.imagem:
                    noticia.imagem = '/media/' + termos[0].termo.imagem.path.split('/media/')[-1]
                else:
                    noticia.imagem = '/static/site/img/logo.png'
                if noticia.notas:
                    noticia.notas += '[Imagem não recuperada]'
                else:
                    noticia.notas = '[Imagem não recuperada]'
                noticia.save()
                print(f'Imagem ({noticia.id} não carregada: {noticia.media}')

        print(f'Total de registros lidos: {tot_lidos}')
        print(f'Total de registros capturados: {tot_scrap}')
