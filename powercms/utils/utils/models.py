# -*- coding: utf-8 -*-
import random
from django.db import models
from django.db.models import signals
from django.conf import settings

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType


def create_token(num=30):
    token = ""
    for x in range(num):
        token += random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return token


def token_age():
    return 60*48 # 48 horas


def valid_token(owner, tk, auto_remove=True):
    token = UserToken.objects.filter(owner=owner, token=tk)
    if token:
        if token[0].valid():
            if auto_remove:
                token[0].delete()
            return True
    return False


class UserToken(models.Model):
    token = models.CharField(max_length=30, primary_key=True, default=create_token)
    owner=models.CharField(max_length=30)
    date_created = models.DateTimeField(auto_now=True)

    def valid(self):
        if self.date_created+timedelta(minutes=token_age()) < datetime.now():
            return False
        return True

    def link(self):
        return '%s/%s?tk=%s' % (settings.SITE_HOST, self.owner, self.token)

    def __str__(self):
        return self.token


# Sempre que um novo token é gerado, a rotina tenta apagar os expirados
def clean_usertoken_post_save(signal, instance, sender, created, **kwargs):
    limite = datetime.now()-timedelta(minutes=token_age())
    cnt = UserToken.objects.filter(date_created__lt=limite).delete()


signals.post_save.connect(clean_usertoken_post_save, sender=UserToken)


def LogObject(object, mensagem):
    user = User.objects.get_or_create(username='sys')[0]
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        object_repr='%s' % object,
        action_flag=CHANGE,
        change_message=mensagem
    )


def LogError(rotina, exception):
    user = User.objects.get_or_create(username='sys')[0]
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(user).pk,
        object_id=user.pk,
        object_repr='%s' % rotina,
        action_flag=ADDITION,
        change_message=exception
    )
