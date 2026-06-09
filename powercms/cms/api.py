from collections import OrderedDict

import requests
from django.conf import settings
from django.http import JsonResponse

from .models import GroupVariable, GroupType


def temperatura(request):
    """Retorna json com a temperatura das coordenadas passadas por parâmetro"""
    # coord lista contendo latitude,longitude
    coordenadas = request.GET.getlist('coord', [])
    dct = {}
    tipo_de_grupo, _ = GroupType.objects.get_or_create(name='TEMPERATURA')

    for coordenada in coordenadas:
        # Tenta pegar a coordenada pela api e atualizar a tabela com a última temperatura consultada.
        # Em caso de erro, retorna a última informação armazanada na base.
        chave = getattr(settings, 'DARK_SKY_KEY', '')
        url = 'https://api.darksky.net/forecast/{0}/{1}/?units=si'.format(chave, coordenada)
        try:
            resp = requests.get(url)
            if resp.status_code == requests.codes.ok:
                resp_dct = resp.json()
                clima_atual = resp_dct.get('currently')
                temp = int(clima_atual.get('temperature'))
                dct[coordenada] = temp
                GroupVariable.objects.update_or_create(
                    grouptype=tipo_de_grupo, key=coordenada, defaults={'value': temp}
                )
            else:
                raise requests.HTTPError('Não foi possível retornar a temperatura')
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError):
            try:
                variavel = GroupVariable.objects.get(grouptype=tipo_de_grupo, key=coordenada)
                dct[coordenada] = variavel.value
            except GroupVariable.DoesNotExist:
                dct[coordenada] = 'Sem Informação'
    return JsonResponse(dct)


def marcador_mapa(request):
    """Retorna um Json com categorias e marcadores para usar em mapas"""
    categorias = OrderedDict()
    marcadores = []
    label = None

    qs = GroupVariable.objects.filter(key='marcador-mapa').order_by('grouptype__order', 'grouptype__pk')

    for marcador in qs:
        if marcador.grouptype.name not in categorias:
            label = chr(len(categorias) + 65)
            categorias[marcador.grouptype.name] = '{0} ({1})'.format(marcador.grouptype.name, label)
        try:
            lat, lng = marcador.value.split(',')
            marcadores.append({
                'lat': lat.strip(), 'lng': lng.strip(), 'label': label, 'title': marcador.grouptype.name,
                'category': categorias[marcador.grouptype.name]
            })
        except ValueError:
            pass
    return JsonResponse({'categorias': categorias.values(), 'marcadores': marcadores})
