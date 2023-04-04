# coding: utf-8
from django.apps import apps as django_apps
from django.contrib.admin.views.main import PAGE_VAR
from django.utils.encoding import force_text
from django.utils.http import urlencode


class SimpleListFilter(object):
    """
    Versão simplificada da classe inspirada em SimpleListFilter do admin, para utilizar em templates fora do admin.
    """

    def __init__(self, request, model_name, parameter_name):
        """
        :param request: HttRequest
        :param model_name: String com o nome da classe no padrão app_label.model_name
        :param parameter_name: Nome do parâmetro utilizado na query string da URL.
        Nesta versão este parâmetro é sempre a chave primária do model.
        """
        self.params = dict(request.GET.items())
        self.model = django_apps.get_model(model_name)
        self.parameter_name = parameter_name
        self.used_parameters = {}

        if PAGE_VAR in self.params:
            del self.params[PAGE_VAR]

        if self.parameter_name in self.params:
            value = self.params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

    def lookups(self):
        """
        Retorna tuplas contendo chave e descrição, onde a chave é o valor que será apresentado na URL
        e a descrição será o nome apresentado no item do filtro.
        Nesta versão retorna todos os registros do model.
        """
        for obj in self.model.objects.all():
            yield (obj.pk, unicode(obj))

    def value(self):
        """Retorna o valor que está no request para o parâmetro do filtro"""
        return self.used_parameters.get(self.parameter_name)

    def choices(self):
        yield {
            'selected': self.value() is None,
            'query_string': self.get_query_string(),
            'display': 'Todas',
        }

        for lookup, title in self.lookups():
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': self.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }

    def get_query_string(self, new_params=None):
        if new_params is None:
            new_params = {}
        p = self.params.copy()
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        return '?%s' % urlencode(sorted(p.items()))
