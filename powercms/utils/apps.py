# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .management import update_contenttypes


class UtilsConfig(AppConfig):
    name = 'powercms.utils'

    def ready(self):
        super(UtilsConfig, self).ready()
        post_migrate.connect(update_contenttypes, dispatch_uid='utils.management.update_contenttypes')
