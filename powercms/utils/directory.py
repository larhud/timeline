# -*- coding: utf-8 -*-
import os
import shutil

from django.conf import settings


class Path():
    def __init__(self):
        self._PJD = settings.PROJECT_DIR

    def make_path(self, list_base_name, make=False, overwrite=False):
        '''
            Cria o caminho absoluto do diretório do projeto com o base_name
            Args:
                list_base_name (list(str)): (exemplo:) /settings.PROJECT_DIR/list_base_name[0:len(list)]/ .
                make_file (bool): True irá tentar criar o path.
                overwrite (bool): Utilizado, juntamente, com o make_file,
                                  se True, caso o arquivo/diretório exista irá sobrescrever o mesmo.
            Returns:
                str: Nome do path absoluto
        '''

        _path = settings.PROJECT_DIR
        for name in list_base_name:
            _path = os.path.join(_path, name)

        if make:
            if overwrite and os.path.exists(_path):
                shutil.rmtree(_path)
            os.makedirs(_path)

        return _path

    def exists(self, path_name, file=False):
        '''
            Verifica a existência do path_name no projeto
            Args:
                path_name (str): Nome do path a ser avaliado.
            Returns:
                bool: True se existe, False caso não exista
        '''

        if os.path.isabs(path_name):
            return os.path.exists(path_name)

        if file:  # Se não for caminho absoluto, assim procura somente na pasta
            return os.path.isfile(path_name)

        return os.path.exists(self.make_path(list_base_name=[path_name]))

    def remove(self, path_name):
        # Segurança: Somente exclui a pasta tmp
        if path_name == self.make_path(['tmp']) and os.path.exists(path_name):
            shutil.rmtree(path_name)
            return True

        return False

    def check_struct(self, path_name, check_fields):

        '''
            Verifica a estrutura de uma pasta
            Args:
                path_name (str): Nome do path (diretório) a ser avaliado.
                check_fields (list(str)): Lista de arquivos/diretórios que devem existir
                                          no path_name
            Returns:
                list: lista com o nome dos campos (passados no check_fields) não econtrados
        '''
        errors = []
        for _path, field in zip([self.make_path(list_base_name=[path_name, p]) for p in check_fields], check_fields):
            if not os.path.exists(_path):
                errors.append(field)

        return errors

    def make_file(self, name, where=None):
        '''
            Cria um arquivo no diretório atual
            Args:
                name (str): Nome do arquivo a ser criado.
                where (str): Nome do diretório onde o arquivo será criado
            Returns:
                int: 1 se criado, 0 caso não criado, -1 caso ocorreu erro
        '''
        try:
            if where and os.path.exists(where):
                os.chdir(where)
            if not self.exists(name, file=True):
                file = open(name, 'w+')
                file.close()
        finally:
            os.chdir(self._PJD)
            return name
