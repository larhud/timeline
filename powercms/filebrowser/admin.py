# -*- coding: utf-8 -*-
from django.contrib import admin

from poweradmin.admin import PowerModelAdmin
from .models import LogEntry


class LogEntryAdmin(PowerModelAdmin):
    list_display = ('object_id', 'action_time', 'user', 'action_flag', 'change_message', )
    list_filter = ('object_id', 'action_time', 'user', 'action_flag', )
    readonly_fields = ('object_id', 'action_time', 'user', 'action_flag', 'change_message', )
    search_fields = ('object_id', 'change_message', )
admin.site.register(LogEntry, LogEntryAdmin)