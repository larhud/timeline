# Generated by Django 2.2.24 on 2022-07-24 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0020_auto_20220503_1147'),
    ]

    operations = [
        migrations.AddField(
            model_name='termo',
            name='imagem',
            field=models.ImageField(blank=True, null=True, upload_to='uploads'),
        ),
    ]