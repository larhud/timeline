from django.contrib.auth.models import User
from django.db import models


class LogEntry(models.Model):
    class Meta:
        verbose_name = 'Histórico de Operações'
        verbose_name_plural = 'Histórico de Operações'
        ordering = ('-action_time',)

    ACTION_FLAG = (
        (1, 'Adicionado'),
        (2, 'Editado'),
        (3, 'Removido'),
    )
    action_time = models.DateTimeField('Hora', auto_now=True)
    user = models.ForeignKey(User, related_name='filebrowser_logentry_set', verbose_name='Usuário',
                             on_delete=models.CASCADE)
    object_id = models.TextField('Arquivo', blank=True, null=True)
    action_flag = models.PositiveSmallIntegerField('Ação', choices=ACTION_FLAG)
    change_message = models.TextField('Alteração', blank=True)

    def __str__(self):
        if self.action_flag == 2:
            return self.change_message
        return self.get_action_flag_display()
