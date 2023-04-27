import os
import requests

import hashlib

from django.core.management.base import BaseCommand
from django.db.transaction import set_autocommit, commit, rollback

from base import save_image, scrap_best_image, load_html
from base.models import Noticia

headers = {'user-agent':
           'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}

host_timeout = {'agenciabrasil.ebc.com.br': 90, 'folhacg.com.br': 30}


class Command(BaseCommand):
    help = 'Verifica se as URLs são válidas'

    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=str, help='Id da Notícia')

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__)).split('/')[:-3]
        base_dir = '/'.join(base_dir)
        id = options['id']
        html_path = os.path.join('/', base_dir, 'media', 'html')
        pdf_path = os.path.join('/', base_dir, 'media', 'pdf')
        if id:
            queryset = Noticia.objects.filter(id=id)
        else:
            queryset = Noticia.objects.filter(url_valida=True, revisado=False).order_by('pk')
        tot_fix = 0
        tot_lidas = 0
        tot_cached = 0
        tot_invalida = 0
        set_autocommit(False)
        for noticia in queryset:
            tot_lidas += 1
            if tot_lidas % 100 == 0:
                print(noticia.id)

            # Testa se a URL está duplicada
            real_hash = hashlib.sha256(noticia.url.encode('utf-8')).hexdigest()
            if real_hash != noticia.url_hash:
                dset = Noticia.objects.filter(url_hash=real_hash).exclude(id=noticia.id)
                if dset.count() != 0:
                    print(f'URL Duplicada {noticia.id_externo} {noticia.url}')

            hostname = noticia.url.split("//")[-1].split("/")[0].split('?')[0]
            timeout = host_timeout.get(hostname,10)

            # Testa se a URL existe
            try:
                response = requests.head(noticia.url, headers=headers, timeout=timeout)
                if response.status_code == 403:
                    response = requests.get(noticia.url, headers=headers, timeout=timeout)
                link_ok = response.status_code == 200
            except Exception as e:
                print(e.__str__())
                link_ok = False
                response = None

            # se o status for Moved Permanent, tentar obter a nova URL
            # muitas vezes o redirect é para a home do site.
            # if response.status_code == 301:
            #    nova_url = response.next.url
            #    response = requests.head(nova_url, timeout=5)
            #    if response.status_code == 200:
            #        noticia.url = nova_url

            if not link_ok:
                # se não existir, verificar se não existe um redirecionamento para outra URL
                if response and response.history:
                    print("Request was redirected")
                    for history in response.history:
                        print(history.status_code, history.url)
                    print("Final destination:")
                    print(response.status_code, response.url)
                else:
                    if noticia.url_valida:
                        noticia.url_valida = False
                        noticia.save()
                        tot_invalida += 1
                        print(f'URL não validada com ID: {noticia.id}')

            else:
                # se a URL está válida, atualizar o status
                if not noticia.url_valida:
                    noticia.url_valida = True
                    noticia.save()
                    tot_fix += 1

                # conferir se o flag do PDF está ok
                if not noticia.pdf_atualizado:
                    cache_filename = os.path.join(pdf_path,f'{noticia.id}.pdf')
                    if os.path.exists(cache_filename):
                        noticia.pdf_atualizado = True
                        noticia.save()

                # conferir se o cache HTML está ok
                cache_filename = os.path.join(html_path,f'{noticia.id}.html')
                if not os.path.exists(cache_filename):
                    if load_html(noticia.url, noticia.id):
                        tot_cached += 1

                commit()

        print(f'Total de notícias lidas: {tot_lidas}')
        print(f'Total de Notícias em HTML {tot_cached}')
        print(f'Total de Notícias inválidas {tot_invalida}')
        print(f'Total de Notícias corrigidas {tot_fix}')

