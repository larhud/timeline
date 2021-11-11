from django.db import models
from cms.models import Recurso
from django_powercms.utils.wordcloud import build_wordcloud


class Termo(models.Model):
    termo = models.CharField(max_length=120, unique=True)
    id_externo = models.BigIntegerField(null=True, blank=True)
    num_reads = models.BigIntegerField('Núm.Acessos', default=0)

    class Meta:
        verbose_name = 'Termo'
        verbose_name_plural = 'Termos'

    def __str__(self):
        return self.termo


class Noticia(models.Model):
    titulo = models.TextField('Título', null=True, blank=True)
    dt = models.DateField()
    url = models.URLField(unique=True)
    texto = models.TextField(null=True, blank=True)
    media = models.URLField('Media', null=True, blank=True)
    fonte = models.CharField('Fonte de Dados', max_length=80, null=True, blank=True)
    nuvem = models.TextField(null=True, blank=True)
    atualizado = models.BooleanField(default=False, null=True, blank=True)

    def gerar_nuvem(self):
        texto = self.texto
        # termos da notícia
        for assunto in self.assunto_set.all():
            texto += ' '+assunto.termo.termo

        stopwords = Recurso.objects.get_or_create(recurso='TAGS-EXC')[0].valor or ''
        stopwords = stopwords.lower()
        stopwords = [ exc.strip() for exc in stopwords.split(',') ] if stopwords else []

        words_compost_frequency = build_wordcloud(texto, stopwords)

        self.nuvem = words_compost_frequency
        self.atualizado = True
        self.save()

    class Meta:
        verbose_name = 'Notícia'
        
    def __str__(self):
        return u'%s' % self.titulo


class AssuntoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('termo')


class Assunto(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE)

    objects = AssuntoManager()

    def __str__(self):
        return '%s' % self.noticia
