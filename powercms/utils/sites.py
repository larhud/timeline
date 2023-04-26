# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site as _get_current_site


def get_current_site(request):
    try:
        return Site.objects.get(domain=request.get_host())
    except Site.DoesNotExist:
        return _get_current_site(request)
