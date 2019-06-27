"""Interfaces de los repositorios para la persistencia de datos.
"""
import abc

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class EntityRepository(abc.ABC):
    """Interfaz de los repositorios de entidades.
    """
    @abc.abstractmethod
    def save(self, entity):
        pass

    @abc.abstractmethod
    def load(self, id):
        pass

    @abc.abstractmethod
    def get_all_ids(self):
        pass

    @abc.abstractmethod
    def check_if_exist(self, id):
        pass
