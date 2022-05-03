from calendar import monthrange

from django import forms
from django.contrib.admin.views.main import ChangeList
from django.core.validators import EMPTY_VALUES
from django.forms import BaseInlineFormSet
from django.utils.datetime_safe import datetime
from django.forms.widgets import NumberInput, URLInput


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


class BuscaArquivoPT(forms.Form):
    busca = forms.CharField(label='Termo de Busca', required=True)
    dtinicial = forms.DateField(label='Data Inicial:', widget=NumberInput(attrs={'type': 'date'}), required=False)
    dtfinal = forms.DateField(label='Data Final:', widget=NumberInput(attrs={'type': 'date'}), required=False)


class AnoMesWidget(forms.MultiWidget):

    def __init__(self, *args, **kwargs):
        widgets = (forms.HiddenInput, forms.HiddenInput)
        super().__init__(widgets, *args, **kwargs)

    def decompress(self, value):
        # É obrigatório implementar este método para funcionar o multi campo.
        return value


class AnoMesField(forms.MultiValueField):
    """Campo que recebe dois valores: Ano, mês e retorna uma lista com o range de data inicial e final do mês/ano"""
    widget = AnoMesWidget

    def __init__(self, *args, **kwargs):
        fields = (forms.CharField(required=False), forms.CharField(required=False))
        super().__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        result = []

        if data_list:
            ano = data_list[0]
            mes = data_list[1]

            if ano not in EMPTY_VALUES and mes not in EMPTY_VALUES:
                data_ini = datetime.strptime(f'01/{mes}/{ano}', '%d/%m/%Y')
                data_fim = datetime(
                    year=data_ini.year, month=data_ini.month, day=monthrange(data_ini.year, data_ini.month)[1]
                )

                result = [data_ini, data_fim]

        return result


class FormBuscaTimeLine(forms.Form):
    """Form utilizado para tratar as condições de filtro da query de notícias"""
    busca = forms.CharField(label='Busca', required=False)
    datafiltro = forms.CharField(label='Data', required=False)
    ano_mes = AnoMesField(label='Ano/Mês', required=False)
    veiculo = forms.CharField(label='Veiculo', required=False)
    termo = forms.CharField(label='Termo', required=False)

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
