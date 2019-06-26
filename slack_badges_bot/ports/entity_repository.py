"""Interfaz de los repositorios destinados a persistir entidades
"""

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class EntityRepositoryPort:

    def save(self, entity):
        raise NotImplementedError

    def load(self, id):
        raise NotImplementedError

    def get_all_ids(self):
        raise NotImplementedError

    def check_if_exist(self, id):
        raise NotImplementedError
