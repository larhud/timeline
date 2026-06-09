# coding:utf-8
#import datetime
import os
from django.utils.text import capfirst


def only_numbers(value):
    # Retorna uma nova string, removendo qualquer caracter que não seja um número
    return ''.join(val for val in value if val.isdigit())


def nvl(objeto, alternativa):
    # simula a função clássica do Oracle: Retorna uma alternativa caso o objeto esteja vazio
    if not objeto:
        return objeto
    else:
        return alternativa


def upper_first(value):
    # Retorna a string capitalizada, considerando preposições em Português
    result = ''
    for sentence in value.split(" "):
        if sentence in ['de', 'da', 'do', 'para', 'e', 'entre']:
            result = result + " " + sentence
        else:
            result = result + " " + capfirst(sentence)
    return result.lstrip()


# Retorna o objeto referenciado no PATH do request
def get_object_from_path(request, model):
    object_id = request.META['PATH_INFO'].strip('/').split('/')[-2]
    if object_id.isdigit():
        return model.objects.get(pk=object_id)
    raise model.DoesNotExist()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def server_status():
    json = {}
    # HD
    devices_data = os.popen('df').read().split('\n')
    header = devices_data[0].split()
    for device in devices_data[1:]:
        if device:
            data = [int(data) if data.isdigit() else data for data in device.split()[1:]]
            json[device.split()[0]] = dict(zip(header[1:], data))
    # Memory
    memory_data = os.popen('free').read().split('\n')
    header = memory_data[0].split()
    for memory in memory_data[1:]:
        if memory:
            data = [int(data) if data.isdigit() else data for data in memory.split()[1:]]
            json[memory.split()[0]] = dict(zip(header, data))
    return json