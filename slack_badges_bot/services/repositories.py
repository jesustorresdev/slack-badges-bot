"""Interfaces de los repositorios para la persistencia de datos.
"""
import abc
import logging
from typing import List

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class EntityRepository(abc.ABC):
    """Interfaz de los repositorios de entidades.
    """
    @property
    @abc.abstractmethod
    def stored_type(self):
        pass

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


class EntityRepositoryFactory:

    def __init__(self, entity_repositories: List[EntityRepository]):
        self.entity_repositories = entity_repositories

    def __call__(self, stored_type):
        for repository in self.entity_repositories:
            if repository.stored_type is stored_type:
                return repository
        raise ValueError(f"Could not find {stored_type}.")
