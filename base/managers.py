import ast
from collections import Counter

from django.core.validators import EMPTY_VALUES
from django.db import models


def add_criteria(dct, opcoes, campo, lookup=None, tipo_lookup='__contains'):
    """
    Atualiza dct com os parâmetros de busca.
    Se lookup for passado, ele será utilizado na montagem do critério de busca.
    Ex.: add_criteria(dct, opcoes, 'nome')
         add_criteria(dct, opcoes, 'nome', lookup='tabela__nome')
         add_criteria(dct, opcoes, 'valor', tipo_lookup='__gte')
    """
    valor = opcoes.get(campo)

    if valor not in EMPTY_VALUES:
        chave = lookup + tipo_lookup if lookup else campo + tipo_lookup
        dct[chave] = valor


class NoticiaQueryset(models.QuerySet):

    def pesquisa(self, **kwargs):
        params = {}
        add_criteria(params, kwargs, 'busca', 'texto')
        add_criteria(params, kwargs, 'datafiltro', 'dt', tipo_lookup='__range')
        add_criteria(params, kwargs, 'ano_mes', 'dt', tipo_lookup='__range')

        return self.filter(**params)

    def anos(self):
        """Retorna uma lista com distinct dos anos da base de notícias"""
        return [r.year for r in self.dates('dt', 'year')]

    def nuvem(self):
        result = Counter()
        for record in self.all():
            nuvem = ast.literal_eval(record.nuvem)
            for termo in nuvem:
                result[termo[0]] += termo[1]
        return result.most_common(30)
