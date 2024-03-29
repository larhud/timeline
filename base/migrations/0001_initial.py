# Generated by Django 2.2.17 on 2021-08-11 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Noticia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('titulo', models.TextField(blank=True, null=True, verbose_name='')),
                ('dt', models.DateField()),
                ('texto', models.TextField(blank=True, null=True)),
                ('nuvem', models.TextField(blank=True, null=True)),
                ('atualizado', models.BooleanField(blank=True, default=False, null=True)),
            ],
            options={
                'verbose_name': 'Notícia',
            },
        ),
        migrations.CreateModel(
            name='Termo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('termo', models.CharField(max_length=120, unique=True)),
                ('id_externo', models.BigIntegerField(blank=True, null=True)),
                ('num_reads', models.BigIntegerField(default=0, verbose_name='Núm.Acessos')),
            ],
            options={
                'verbose_name': 'Termo',
                'verbose_name_plural': 'Termos',
            },
        ),
        migrations.CreateModel(
            name='Assunto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noticia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Noticia')),
                ('termo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Termo')),
            ],
        ),
    ]
