# Generated by Django 2.2.24 on 2022-04-19 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_auto_20220311_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticia',
            name='id_externo',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
    ]