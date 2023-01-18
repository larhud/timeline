import os
import requests


# Rotina salva a imagem indicada na URL no path indicado.
# A tipo da imagem é "calculado" e incluído ao path
def save_image(url, full_path, id_noticia):
    server_filename = url.split('/')[-1]
    file_ext = server_filename.split('.')[ -1 ].split('?')[ 0 ]
    if len(file_ext) > 4 or len(file_ext) == 0 or file_ext == 'img':
        file_ext = 'jpeg'
    full_path += '/%d.%s' % (id_noticia, file_ext)
    try:
        headers = {'user-agent':
                   'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(full_path, 'wb') as file:
                file.write(response.content)
            relative_path = '/media/img/'+full_path.split('/')[-1]
        else:
            relative_path = None
    except Exception as e:
        relative_path = None
    return relative_path


