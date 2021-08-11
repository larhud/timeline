import os

from django import forms
from django.contrib.admin.views.main import ChangeList

from django.forms import BaseInlineFormSet


class LinhaFormSet(BaseInlineFormSet):
    def full_clean(self):
        """
                Clean all of self.data and populate self._errors and
                self._non_form_errors.
                """
        self._errors = []
        self._non_form_errors = self.error_class()

        self.clean()


class InlineChangeList(object):
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__['get_query_string']

    def __init__(self, request, page_num, paginator):
        self.show_all = 'all' in request.GET
        self.page_num = page_num
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = dict(request.GET.items())


class FormImportacaoVC(forms.Form):
    arquivo = forms.FileField()

