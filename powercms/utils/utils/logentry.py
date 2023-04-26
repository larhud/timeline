from datetime import datetime

from django.contrib.admin.models import LogEntry


class LogEntryMixin:
    def make_log(self, content_type_id, object_repr, object_id, change_message, user=None):
        lg = LogEntry()
        lg.action_time = datetime.now()
        lg.user = user
        lg.content_type_id = content_type_id
        lg.object_repr = object_repr
        lg.object_id = object_id
        lg.action_flag = True
        lg.change_message = change_message
        lg.save()
