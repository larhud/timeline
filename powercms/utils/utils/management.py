# coding:utf-8
from django.apps import apps as django_apps
from django.db import DEFAULT_DB_ALIAS


def update_contenttypes(app_config, verbosity=2, interactive=False, using=DEFAULT_DB_ALIAS, apps=django_apps, **kwargs):
    if not app_config.models_module:
        return

    app_label = app_config.label

    try:
        contenttype_cls = apps.get_model('contenttypes', 'ContentType')
    except LookupError:
        return