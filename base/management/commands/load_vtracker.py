import datetime
import hashlib
import logging
import os
import time

from csv import DictReader
from django.conf import settings
from django.core.management.base import BaseCommand
from base.models import Noticia, Termo, Assunto
from timeline.settings import noticia_imagem_path
from base import save_image, scrap_best_image, load_html

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-3.3s] %(message)s",
    handlers=[
        logging.FileHandler("load_vtracker.log", mode='a'),
        logging.StreamHandler()
    ]
)

headers = {'user-agent':
           'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}

host_timeout = {'agenciabrasil.ebc.com.br': 90, 'folhacg.com.br': 30}


class Command(BaseCommand):
    help = 'Carrega as notícias do VTracker via CSV'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--timeline', type=int, help='Id da Timeline', required=True)

    def handle(self, *args, **options):
        tot_lidos = 0
        tot_scrap = 0
        timeline = Termo.objects.filter(pk=options['timeline'])
        if timeline.count() == 0:
            print(f'Timeline %d não encontrada' % options['timeline'])
        timeline = timeline[0]

        time_begin = time.time()
        img_path = noticia_imagem_path()
        filename = os.path.join(settings.BASE_DIR, 'data', 'posts_com_tags.csv')
        file = open(filename, 'r', encoding='utf-8')
        logging.info(f'Processando arquivo {filename}')

        # dt	titulo	url	texto	media	fonte
        reader = DictReader(file, delimiter=',', quotechar='"')
        for line in reader:
            tot_lidos += 1
            dt = datetime.datetime.strptime(line['dt'], "%Y-%m-%d")
            titulo = line['titulo']
            url = line['url']
            fonte = line['fonte']
            url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
            noticia = Noticia.objects.filter(url_hash=url_hash).first()
            if not noticia:
                noticia = Noticia(dt=dt, titulo=titulo, url=url, fonte=fonte, url_valida=False,
                                  id_externo=tot_lidos, origem=1, revisado=True)

            noticia.texto = line['texto'].strip()
            noticia.texto_completo = line['texto'].strip()
            noticia.atualizado = True
            noticia.visivel = True
            noticia.save()
            assunto = Assunto(termo=timeline, noticia=noticia, id_externo=tot_lidos)
            assunto.save()

            # Validando a URL
            hostname = noticia.url.split("//")[-1].split("/")[0].split('?')[0]
            timeout = host_timeout.get(hostname, 10)

            # Testa se a URL existe
            try:
                imagem_ok = False
                soup = load_html(noticia.url, noticia.id, True, timeout)
                if soup:
                    noticia.url_valida = True
                    imagem_url = scrap_best_image(soup)
                    if imagem_url:
                        file_path = save_image(imagem_url, img_path, noticia.id)
                        if file_path:
                            tot_scrap += 1
                            noticia.imagem = file_path
                            noticia.notas = None
                            imagem_ok = True

                if not imagem_ok:
                    noticia.notas = '[Imagem não recuperada]'
                    noticia.imagem = '/static/site/img/logo.png'

                noticia.revisada = True
                noticia.save()

            except Exception as e:
                logging.error(f'Noticia {noticia.id}')
                logging.error(e.__str__())

        time_end = time.time()
        t = time_end - time_begin
        print(f'Total de registros lidos: {tot_lidos}')
        print(f'Total de registros capturados: {tot_scrap}')
        logging.info('Tempo de Processamento: %s minutos' % (round(t / 60, 2)))