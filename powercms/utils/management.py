# coding:utf-8
from django.apps import apps as django_apps
from django.db import DEFAULT_DB_ALIAS
from django.utils.encoding import smart_text


def update_contenttypes(app_config, verbosity=2, interactive=False, using=DEFAULT_DB_ALIAS, apps=django_apps, **kwargs):
    if not app_config.models_module:
        return

    app_label = app_config.label

    try:
        contenttype_cls = apps.get_model('contenttypes', 'ContentType')
    except LookupError:
        return

    try:
        for ct in contenttype_cls.objects.db_manager(using).filter(app_label=app_label):
            name = smart_text(ct.model_class()._meta.verbose_name_raw)
            if ct.name != name:
                print("Updating ContentType's name: '%s' -> '%s'" % (ct.name, name))
                ct.name = name
                ct.save()
    except:
        pass
