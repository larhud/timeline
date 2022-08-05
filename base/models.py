import hashlib

from cms.models import Recurso
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from base.managers import NoticiaQueryset, test_url, build_wordcloud, AssuntoManager


class Termo(models.Model):
    termo = models.CharField(max_length=120, unique=True)
    texto_explicativo = models.TextField(null=True)
    slug = models.CharField(max_length=60, null=True)
    imagem = models.ImageField(upload_to='uploads', null=True, blank=True)
    visivel = models.BooleanField('Visível', default=True)
    num_reads = models.BigIntegerField('Núm.Acessos', default=0)

    class Meta:
        verbose_name = 'Termo'
        verbose_name_plural = 'Termos'

    def __str__(self):
        return self.termo

    def tot_noticias(self):
        return self.assunto_set.count() or 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.termo)[:60]
        super(Termo, self).save(*args, **kwargs)

    tot_noticias.short_description = "Total de Notícias"


URL_MAX_LENGTH = 500
TIPOS_ORIGEM = ((0, 'Manual'), (1, 'CSV'), (2, 'Arquivo PT'), (3, 'Twitter'), (4, 'Google Acadêmico'))


class Noticia(models.Model):
    dt = models.DateField(db_index=True)
    url = models.URLField(max_length=URL_MAX_LENGTH)
    url_hash = models.CharField(max_length=64, unique=True)
    url_valida = models.BooleanField('URL Válida', default=False)
    atualizado = models.BooleanField('Texto atualizado', default=False)
    revisado = models.BooleanField('Texto revisado', default=False)
    pdf_atualizado = models.BooleanField('PDF gerado', default=False)
    visivel = models.BooleanField('Visível ao público', default=True)
    titulo = models.TextField('Título')
    texto = models.TextField('Texto Base', null=True, blank=True)
    media = models.URLField('Imagem', max_length=400, null=True, blank=True)
    imagem = models.CharField('Imagem Local', max_length=200, null=True, blank=True)
    fonte = models.CharField('Fonte da Notícia', max_length=80, null=True, blank=True)
    origem = models.IntegerField(default=0, choices=TIPOS_ORIGEM)
    texto_completo = models.TextField('Texto Completo', null=True, blank=True)
    nuvem = models.TextField(null=True, blank=True)
    texto_busca = models.TextField(null=True, blank=True)
    id_externo = models.IntegerField(null=True, blank=True, db_index=True)
    notas = models.TextField(blank=True, null=True)

    objects = NoticiaQueryset.as_manager()

    def gerar_nuvem(self):
        texto = '%s %s %s' % (self.texto_completo, self.texto, self.titulo)
        if not texto:
            return None, None
        for assunto in self.assunto_set.all():
            texto += ' ' + assunto.termo.termo

        stopwords = Recurso.objects.get_or_create(recurso='TAGS-EXC')[0].valor or ''
        stopwords = stopwords.lower()
        stopwords = [exc.strip() for exc in stopwords.split(',')] if stopwords else []
        return build_wordcloud(texto, [], stopwords)

    class Meta:
        verbose_name = 'Notícia'
        ordering = ('dt',)

    def __str__(self):
        return u'%s' % self.titulo

    @property
    def imagem_final(self):
        if self.imagem:
            if self.imagem[0] == '/':
                return self.imagem
            else:
                return '/'+self.imagem
        elif self.media:
            return self.media
        else:
            return '/media/img/66.jpg'

    def pdf_file(self):
        if self.pdf_atualizado:
            return mark_safe(f'<a href="/media/pdf/{self.id}.pdf" target="_blank">Baixar Arquivo</a>')
        else:
            return ''

    pdf_file.short_description = 'PDF Atual'

    def save(self, *args, **kwargs):
        if not self.url_hash:
            self.url_hash = hashlib.sha256(self.url.encode('utf-8')).hexdigest()

        if not self.url_valida and self.visivel:
            self.url_valida = test_url(self.url)

        if 'form' in kwargs:
            form = kwargs['form']
            del kwargs['form']
        else:
            form = None
        update_image = form and self.imagem and 'image' in form.changed_data

        # só monta a nuvem se o texto fo visivel e ainda não estiver marcado como revisado
        if not self.visivel or self.revisado:
            if not self.revisado:
                self.texto_busca = None
                self.nuvem = None
        else:
            nuvem, nuvem_sem_bigramas = self.gerar_nuvem()
            if nuvem:
                # Retorna apenas as palavras que tenham frequência > 2
                # ou então toda a lista caso todos tenham frequência menor que 2
                limit = 0
                for word, cnt in nuvem.most_common():
                    if cnt > 2:
                        limit += 1
                    else:
                        break
                if limit == 0: limit = None
                self.nuvem = nuvem.most_common(limit)
                busca = ''
                for item,count in nuvem_sem_bigramas.most_common():
                    busca += item+' '
                self.texto_busca = busca
        super(Noticia, self).save(*args, **kwargs)

        # TODO: refazer via post_save
        # if not self.imagem and self.media:
        #    self.media = save_image(noticia_imagem_path(), self.id)
        #    super(Noticia, self).save(*args, **kwargs)


class Assunto(models.Model):
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE)
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE)
    id_externo = models.IntegerField(null=True, blank=True)

    objects = AssuntoManager()

    class Meta:
        indexes = [
            models.Index(fields=['termo', 'id_externo'], name='termo_idx'),
        ]

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
