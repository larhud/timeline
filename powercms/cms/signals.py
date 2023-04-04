# -*- coding: utf-8 -*-

from django.template.defaultfilters import slugify


def slug_pre_save(signal, instance, sender, **kwargs):
    if hasattr(instance, 'slug_conf') and not getattr(instance, instance.slug_conf['field'], None):
        slug = slugify(getattr(instance, instance.slug_conf['from'], None))
        new_slug = slug
        counter = 0
        while sender.objects.filter(slug=new_slug).exclude(id=instance.id).count() > 0:
            counter += 1
            new_slug = '%s-%d' % (slug, counter)
        setattr(instance, instance.slug_conf['field'], new_slug)
