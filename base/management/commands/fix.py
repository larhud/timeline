import os
import logging
import requests

import hashlib

from django.core.management.base import BaseCommand
from django.db.transaction import set_autocommit, commit, rollback

from base import save_image, scrap_best_image, load_html
from base.models import Noticia, Assunto


class Command(BaseCommand):
    help = 'Verifica se as URLs são válidas'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--timeline', type=int, help='Id da Timeline', required=True)

    def handle(self, *args, **options):

        tot_lidas = 0
        for noticia in Noticia.objects.filter(assunto__termo=options['timeline']):
            tot_lidas += 1
            noticia.texto = noticia.texto.split('.')[0]
            noticia.revisado = True
            noticia.save()
            dset = Assunto.objects.filter(noticia=noticia)
            if dset.count() > 1:
                for record in dset[1:]:
                    record.delete()

