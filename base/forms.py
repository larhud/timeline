from django import forms
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.forms import BaseInlineFormSet
from django.utils.datetime_safe import datetime


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


class FormImportacaoCSV(forms.Form):
    timeline = forms.CharField(label='Linha do Tempo', required=True)
    arquivo = forms.FileField(label='', widget=forms.ClearableFileInput(attrs={'accept': '.csv'}), required=True)


class IntervaloNoticias(forms.Form):
    dataInicial = forms.DateField()
    dataFinal = forms.DateField()


class FormBusca(forms.Form):
    busca = forms.CharField(label='Busca', required=True)


class FormBuscaTimeLine(forms.Form):
    """Form utilizado para tratar as condições de filtro da query de notícias"""
    busca = forms.CharField(label='Busca', required=False)
    datafiltro = forms.CharField(label='Data', required=False)

    def clean_datafiltro(self):
        """Este campo espera texto no padrão dd/mm/yyyy - dd/mm/yyyy e converte para uma lista de datas"""
        data = self.cleaned_data.get('datafiltro')

        if data not in EMPTY_VALUES:
            try:
                lista = data.split(' - ')
                lista[0] = datetime.strptime(lista[0], '%d/%m/%Y')
                lista[1] = datetime.strptime(lista[1], '%d/%m/%Y')
            except (IndexError, ValueError):
                lista = []
        else:
            lista = []

        return lista
