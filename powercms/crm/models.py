# -*- coding: utf-8 -*-
from django.db import models


STATUS_EMAIL = (
    ('A', 'Ativo'), ('N', 'Não confirmado'), ('I', 'Inválido'),
    ('S', 'Spam'), ('O', 'Opt-out')
)


class Contato(models.Model):
    nome = models.CharField('Nome', max_length=255)
    email = models.EmailField('E-mail', unique=True)
    status_email = models.CharField(
        'Status Email', max_length=1,
        choices=STATUS_EMAIL,
        default=STATUS_EMAIL[1][0]
    )

    def __str__(self):
        return self.nome
