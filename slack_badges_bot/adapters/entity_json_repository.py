"""Clase base de los repositorios destinados a persistir entidades en formato JSON
"""
from dataclasses import asdict
from pathlib import Path

from slack_badges_bot.ports.entity_repository import EntityRepositoryPort

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class EntityJsonRepositoryAdapter(EntityRepositoryPort):
    FILENAME_TEMPLATE = '{id}.json'

    def __init__(self, path: Path):
        self.path = path

    def save(self, entity):
        pass

    def load(self, id):
        pass

    def get_all_ids(self):
        return [name.stem for name in self.path.glob(self.FILENAME_TEMPLATE.format(id='*'))]

    def check_if_exist(self, id):
        filepath = self.path / self.FILENAME_TEMPLATE.format(id=id)
        return filepath.exists()
