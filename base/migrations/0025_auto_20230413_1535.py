# Generated by Django 3.2.18 on 2023-04-13 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_noticia_coletanea'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='termo',
            options={'verbose_name': 'Timeline', 'verbose_name_plural': 'Timelines'},
        ),
        migrations.AlterField(
            model_name='termo',
            name='termo',
            field=models.CharField(max_length=120, unique=True, verbose_name='Timeline'),
        ),
    ]
