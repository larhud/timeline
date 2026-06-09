# -*- encoding: utf-8 -*-
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article


class StaticSitemap(Sitemap):
    priority = 0.5
    lastmod = None

    def items(self):
        return [
            (reverse('home'), "daily"),
            (reverse('search'), "daily"),
        ]

    def location(self, obj):
        return obj[0] if isinstance(obj, tuple) else obj

    def changefreq(self, obj):
        return obj[1] if isinstance(obj, tuple) else "monthly"


class ArticleSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at

    def items(self):
        return Article.objects.active()


sitemaps = dict(
    static=StaticSitemap,
    articles=ArticleSitemap,
)
