# coding: utf-8
import os

from ckeditor_uploader.utils import is_valid_image_extension, get_media_url, get_thumb_filename
from ckeditor_uploader.views import browse as bs
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.cache import never_cache


def get_files_dct(user=None):
    def path_to_dict(path):
        if os.path.isdir(path):
            d = {
                'name': os.path.basename(path),
                'path': path.replace(ckeditor_upload_path, ''),
                'type': "folder"
            }
            items = []
            for sub in os.listdir(path):
                item = path_to_dict(os.path.join(path, sub))
                if item:
                    items.append(item)
            d['items'] = items
            return d
        elif '_thumb' not in path and is_valid_image_extension(path):
            # URL for uploaded files
            file_url = path.replace(default_storage.location, '')
            d = {
                'name': os.path.basename(path),
                'path': path.replace(ckeditor_upload_path, ''),
                'thumb': get_media_url(get_thumb_filename(file_url)),
                'src': get_media_url(file_url),
                'size': os.path.getsize(path),
                'type': "file"
            }
            return d

    """
    Recursively walks all dirs under upload dir and generates a list of
    full paths for each file found.
    """
    # If a user is provided and CKEDITOR_RESTRICT_BY_USER is True,
    # limit images to user specific path, but not for superusers.
    if user and not user.is_superuser and getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False):
        user_path = user.username
    else:
        user_path = ''
    # Absolute filesystem path to the directory that will hold uploaded files.
    ckeditor_upload_path = os.path.abspath(os.path.join(default_storage.location, settings.CKEDITOR_UPLOAD_PATH))
    browse_path = os.path.join(ckeditor_upload_path, user_path)

    return path_to_dict(browse_path)


def get_files_gcloud(lista):
    l = {
        'name': '',
        'path': '/media',
        'type': 'folder',
        'items': []
    }
    for file in lista:
        l['items'].append({
            'name': os.path.basename(file.name),
            'path': file.public_url,
            'type': "file",
            'src': file.public_url,
            'thumb': file.public_url,
            'size': file.size
        })

    return l


@never_cache
@staff_member_required
def browse(request):
    if request.GET.get('type') == 'json':
        response = JsonResponse(get_files_dct(request.user))
    else:
        response = bs(request)
    return response
