# Generated by Django 3.2.25 on 2024-10-18 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0026_auto_20230705_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='termo',
            name='stopwords',
            field=models.TextField(blank=True, null=True),
        ),
    ]
