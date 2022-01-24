from django.db import models


class NoticiaQueryset(models.QuerySet):

    def pesquisa(self, **kwargs):
        params = {}

        texto = kwargs.get('busca')
        data = kwargs.get('datafiltro')

        if texto:
            params['texto__contains'] = texto

        if data:
            params['dt__range'] = data

        return self.filter(**params)
