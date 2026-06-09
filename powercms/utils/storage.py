# -*- coding: utf-8 -*-
from django.core.files.storage import FileSystemStorage
from django.utils.text import get_valid_filename
from django.template.defaultfilters import slugify

import os
import uuid


class SpecialCharFileSystemStorage(FileSystemStorage):
    """
    Remove Special Char filesystem storage
    """

    def get_valid_name(self, name):
        nome, extensao = os.path.splitext(name)
        return os.path.join(slugify(get_valid_filename(nome)) + extensao.lower())


class UuidFileSystemStorage(FileSystemStorage):

    def get_valid_name(self, name):
        nome, extensao = os.path.splitext(name)
        return os.path.join(str(uuid.uuid4()) + extensao.lower())
