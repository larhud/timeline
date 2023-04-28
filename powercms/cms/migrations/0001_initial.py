# Generated by Django 3.2.18 on 2023-04-13 12:27

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mptt.fields
import powercms.cms.fields
import smart_selects.db_fields
import uuid


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Título')),
                ('slug', models.SlugField(blank=True, max_length=250, unique=True, verbose_name='slug')),
                ('header', models.TextField(blank=True, null=True, verbose_name='Chamada')),
                ('content', models.TextField(blank=True, null=True, verbose_name='Conteúdo')),
                ('keywords', models.TextField(blank=True, null=True, verbose_name='Palavras Chaves')),
                ('created_at', models.DateField(default=django.utils.timezone.now, verbose_name='Dt.Criação')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Dt.Alteração')),
                ('is_active', models.BooleanField(default=True, verbose_name='Está ativo?')),
                ('allow_comments', models.CharField(choices=[('A', 'Permite comentários'), ('P', 'Permite comentários privados'), ('F', 'Fechado para novos comentários'), ('N', 'Sem comentários')], default='N', max_length=1, verbose_name='Comentários')),
                ('views', models.BigIntegerField(default=0, verbose_name='Visualizações')),
                ('conversions', models.BigIntegerField(default=0, verbose_name='Conversões')),
                ('likes', models.BigIntegerField(default=0, verbose_name='Gostei')),
                ('search', models.TextField(blank=True, null=True)),
                ('og_title', models.CharField(blank=True, max_length=250, null=True, verbose_name='og-titulo')),
                ('og_image', models.ImageField(blank=True, null=True, upload_to='articles', verbose_name='og-imagem')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
            ],
            options={
                'verbose_name': 'Artigo',
                'ordering': ['-created_at'],
                'permissions': (('manage_articles', 'Administrar artigos'),),
            },
        ),
        migrations.CreateModel(
            name='EmailAgendado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(default='', max_length=90)),
                ('status', models.CharField(choices=[('A', 'Aguardando envio manual...'), ('S', 'Enviando...'), ('R', 'Re-enviando'), ('E', 'Erro ao enviar'), ('K', 'Enviado')], default='S', max_length=1)),
                ('date', models.DateTimeField(default=datetime.datetime.now)),
                ('to', powercms.cms.fields.ListField()),
                ('html', models.TextField()),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='GroupType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Nome')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='Ordem')),
            ],
            options={
                'verbose_name': 'Tipo de Grupo',
                'verbose_name_plural': 'Tipos de Grupo',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Recurso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recurso', models.CharField(choices=[('EMAIL', 'Envio de email automático'), ('SITE_NAME', 'Nome do Site'), ('ROBOTS', 'Permite busca pelo Google'), ('COMMENT_P', 'Texto para comentários privados'), ('COMMENT', 'Texto para comentários'), ('SIGNUP', 'Permite cadastro de usuários'), ('EMAILADMIN', 'Quem recebe avisos de novos usuários'), ('CAPTCHA_PU', 'RECAPTCHA_PUBLIC_KEY'), ('CAPTCHA_PR', 'RECAPTCHA_PRIVATE_KEY'), ('OG-IMAGE', 'og-imagem'), ('TAGS', 'Nuvem de Tags'), ('TAGS-EXC', 'Excluir tags da núvem de tags (separar por virgula)'), ('TAGS-FIXA', 'Tags Fixas (separar por virgula)'), ('FACEBOOK', 'Facebook app id')], max_length=10, unique=True, verbose_name='Parâmetro')),
                ('valor', models.TextField(blank=True, null=True, verbose_name='Valor')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?')),
            ],
            options={
                'verbose_name': 'Parâmetro do Site',
                'verbose_name_plural': 'Parâmetros do Site',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Título')),
                ('slug', models.SlugField(blank=True, max_length=250, verbose_name='Slug')),
                ('header', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('keywords', models.TextField(blank=True, default=None, null=True, verbose_name='Palavras Chaves')),
                ('order', models.PositiveIntegerField(db_index=True, default=1, help_text='0 para que a seção não apareça em nenhuma listagem.', verbose_name='Ordem')),
                ('template', models.CharField(blank=True, max_length=250, null=True, verbose_name='Template')),
                ('views', models.IntegerField(default=0)),
                ('conversions', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Seção',
                'verbose_name_plural': 'Seções',
                'ordering': ['order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='Nome')),
                ('path_name', models.SlugField(max_length=60, unique=True, verbose_name='Pasta')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('active', models.BooleanField(default=False, verbose_name='Ativo?')),
                ('path', models.FilePathField(editable=False, max_length=256, path='/home/josir/bitbucket/timeline/media/uploads/themes', recursive=True)),
            ],
            options={
                'verbose_name': 'Temas',
                'verbose_name_plural': 'Temas',
            },
        ),
        migrations.CreateModel(
            name='URLMigrate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_url', models.CharField(db_index=True, max_length=250, verbose_name='URL antiga')),
                ('new_url', models.CharField(max_length=250, verbose_name='URL nova')),
                ('dtupdate', models.DateTimeField(auto_now=True, verbose_name='Última atualização')),
                ('views', models.IntegerField(default=0, editable=False, verbose_name='Visitas')),
                ('redirect_type', models.CharField(choices=[('M', 'MOVED'), ('H', 'HOTLINK')], max_length=1, verbose_name='Tipo')),
                ('obs', models.TextField(blank=True, null=True, verbose_name='Observação')),
            ],
            options={
                'verbose_name': 'Migração de URL',
                'verbose_name_plural': 'Migração de URLs',
            },
        ),
        migrations.CreateModel(
            name='URLNotFound',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('count', models.BigIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-update_at',),
            },
        ),
        migrations.CreateModel(
            name='SectionItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, default=1, verbose_name='Ordem')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.article', verbose_name='Artigo')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.section', verbose_name='Seção')),
            ],
            options={
                'verbose_name': 'Artigo da seção',
                'verbose_name_plural': 'Artigos da seção',
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='section',
            name='articles',
            field=models.ManyToManyField(blank=True, through='cms.SectionItem', to='cms.Article'),
        ),
        migrations.CreateModel(
            name='Permissao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.section')),
            ],
            options={
                'verbose_name': 'Permissão',
                'verbose_name_plural': 'Permissões',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nome')),
                ('link', models.CharField(blank=True, max_length=250, null=True, verbose_name='URL')),
                ('is_active', models.BooleanField(default=True, verbose_name='Está ativo?')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('article', smart_selects.db_fields.ChainedForeignKey(blank=True, chained_field='section', chained_model_field='sections', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.article', verbose_name='Artigo')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='cms.menu', verbose_name='Pai')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.section', verbose_name='Seção')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GroupVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=200)),
                ('grouptype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.grouptype')),
            ],
            options={
                'verbose_name': 'Variável',
                'verbose_name_plural': 'Variáveis',
            },
        ),
        migrations.CreateModel(
            name='GroupItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('grouptype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.grouptype')),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Itens',
                'ordering': ('grouptype__name', 'group__name'),
            },
        ),
        migrations.CreateModel(
            name='FileDownload',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=250, verbose_name='Título')),
                ('file', models.FileField(upload_to='uploads', verbose_name='Arquivo')),
                ('count', models.IntegerField(default=0, verbose_name='Downloads')),
                ('expires_at', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Data de expiração')),
                ('create_article', models.BooleanField(default=False, verbose_name='Criação do Artigo')),
                ('article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.article')),
            ],
            options={
                'verbose_name': 'Arquivo para download',
                'verbose_name_plural': 'Arquivos para download',
            },
        ),
        migrations.CreateModel(
            name='ArticleComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Dt.Criação')),
                ('author', models.CharField(max_length=60, verbose_name='Autor')),
                ('comment', models.TextField(verbose_name='Comentário')),
                ('active', models.BooleanField(default=False, verbose_name='Ativo')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.article', verbose_name='Artigo')),
            ],
            options={
                'verbose_name': 'Comentário',
                'verbose_name_plural': 'Comentários',
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='ArticleAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attrib', models.CharField(max_length=30, verbose_name='Atributo')),
                ('value', models.CharField(max_length=300, verbose_name='Valor')),
                ('active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.article', verbose_name='Artigo')),
            ],
            options={
                'verbose_name': 'Atributo do Artigo',
                'verbose_name_plural': 'Atributos do Artigo',
            },
        ),
        migrations.CreateModel(
            name='ArticleArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.TextField(blank=True, null=True, verbose_name='Chamada')),
                ('content', models.TextField(blank=True, null=True, verbose_name='Conteúdo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Dt.Alteração')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.article', verbose_name='Artigo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
            ],
            options={
                'verbose_name': 'Versão do Artigo',
                'verbose_name_plural': 'Versões dos Artigos',
                'ordering': ('updated_at',),
            },
        ),
        migrations.AddField(
            model_name='article',
            name='sections',
            field=models.ManyToManyField(blank=True, through='cms.SectionItem', to='cms.Section'),
        ),
    ]
