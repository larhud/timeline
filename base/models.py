import hashlib

from cms.models import Recurso
from django.db import models
from django.utils.text import slugify
from django_powercms.utils.wordcloud import build_wordcloud

from base.managers import NoticiaQueryset


class Termo(models.Model):
    termo = models.CharField(max_length=120, unique=True)
    id_externo = models.BigIntegerField(null=True, blank=True)
    num_reads = models.BigIntegerField('Núm.Acessos', default=0)

    class Meta:
        verbose_name = 'Termo'
        verbose_name_plural = 'Termos'

    def __str__(self):
        return self.termo

    def tot_noticias(self):
        return self.assunto_set.count() or 0
    tot_noticias.short_description = "Total de Notícias"

URL_MAX_LENGTH = 500


class Noticia(models.Model):
    dt = models.DateField(db_index=True)
    url = models.URLField(max_length=URL_MAX_LENGTH)
    url_hash = models.CharField(max_length=64, unique=True)
    titulo = models.TextField('Título')
    texto = models.TextField('Texto Base', null=True, blank=True)
    media = models.URLField('Media', max_length=400, null=True, blank=True)
    fonte = models.CharField('Fonte de Dados', max_length=80, null=True, blank=True)
    nuvem = models.TextField(null=True, blank=True)
    texto_completo = models.TextField('Texto Completo', null=True, blank=True)
    atualizado = models.BooleanField(default=False, null=True, blank=True)

    objects = NoticiaQueryset.as_manager()

    def gerar_nuvem(self):
        if self.texto:
            texto = self.texto
            # termos da notícia
            for assunto in self.assunto_set.all():
                texto += ' ' + assunto.termo.termo

            stopwords = Recurso.objects.get_or_create(recurso='TAGS-EXC')[0].valor or ''
            stopwords = stopwords.lower()
            stopwords = [exc.strip() for exc in stopwords.split(',')] if stopwords else []
            return build_wordcloud(texto, stopwords)
        else:
            return None

    class Meta:
        verbose_name = 'Notícia'
        ordering = ('dt',)

    def __str__(self):
        return u'%s' % self.titulo

    def save(self, *args, **kwargs):
        self.url_hash = hashlib.sha256(self.url.encode('utf-8')).hexdigest()
        self.nuvem = self.gerar_nuvem()
        super(Noticia, self).save(*args, **kwargs)


class AssuntoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('termo')


class Assunto(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE)

    objects = AssuntoManager()

    def __str__(self):
        return '%s' % self.noticia


class Busca(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=20, db_index=True)
    count = models.IntegerField()
    busca = models.TextField()

    def __str__(self):
        return '%s' % self.busca

    def save(self, *args, **kwargs):
        self.hash = slugify(self.busca)
        self.count = 0
        super(Busca, self).save(*args, **kwargs)
