# Generated by Django 2.2.24 on 2022-03-11 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_auto_20220311_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticia',
            name='imagem',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Imagem Local'),
        ),
    ]
