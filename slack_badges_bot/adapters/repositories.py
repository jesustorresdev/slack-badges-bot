"""Repositorios para la persistencia de datos.
"""
import json
import dataclasses
from pathlib import Path

from slack_badges_bot.services.repositories import EntityRepository

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class EntityJsonRepository(EntityRepository):
    """Clase de los repositorios destinados a persistir entidades en formato JSON

    :param path: Ruta dónde almacenar los archivos.
    :param entity_type: Clase de la entidad almacenada en el repositorio.
    """
    FILENAME_TEMPLATE = '{id}.json'

    def __init__(self, path: Path, entity_type):
        self.path = path
        self.entity_type = entity_type

    def save(self, entity, overwrite=False):
        filepath = self._build_filepath(id)
        mode = "w" if overwrite else "wx"
        with filepath.open(mode) as f:
            json.dump(dataclasses.asdict(entity), f)

    def load(self, id):
        filepath = self._build_filepath(id)
        with filepath.open("r") as f:
            return self.entity_type(**json.load(f))

    def get_all_ids(self):
        return [name.stem for name in self.path.glob(self.FILENAME_TEMPLATE.format(id='*'))]

    def check_if_exist(self, id):
        filepath = self._build_filepath(id)
        return filepath.exists()

    def _build_filepath(self, id):
        return self.path / self.FILENAME_TEMPLATE.format(id=id)
