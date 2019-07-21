"""Repositorios para la persistencia de datos.
"""
import json
import dataclasses
import uuid

from pathlib import Path
from typing import Type

from slack_badges_bot.services.repositories import EntityRepository

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


def json_dump_default(o):
    """Función para pasar por el argumento default a la función json.dump().

    Añade soporte para atributos UUID en la codificación a JSON. Estos atributos se codifican en formato URN para
    facilitar su identificación posterior a la hora de decodificarlos.
    """
    if isinstance(o, uuid.UUID):
        return o.urn
    if isinstance(o, Path):
        return str(o)
    raise TypeError()


def json_load_object_hook(d):
    """Función para pasar por el argumento object_hook a la función json.load() para añadir soporte para atributos UUID.

    Añade soporte para atributos UUID en la decodificación de JSON. Se espera que estos atributos hayan sido codificados
    en formato URN.
    """
    return {key: uuid.UUID(value) if str(value).startswith("urn:uuid:") else value for key, value in d.items()}


class EntityJsonRepository(EntityRepository):
    """Clase de los repositorios destinados a persistir entidades en formato JSON

    :param stored_type: Clase de la entidad almacenada en el repositorio.
    :param path: Ruta dónde almacenar los archivos.
    """
    FILENAME_TEMPLATE = '{id}.json'

    def __init__(self, stored_type: Type, path: Path):
        self._stored_type = stored_type
        self.path = path

    @property
    def stored_type(self):
        return self._stored_type

    def save(self, entity, overwrite=False):
        filepath = self._build_filepath(entity.id.hex)
        mode = "w" if overwrite else "x"
        with filepath.open(mode) as f:
            json.dump(dataclasses.asdict(entity), f, default=json_dump_default)

    def load(self, id):
        filepath = self._build_filepath(id)
        with filepath.open("r") as f:
            json_loaded = json.load(f, object_hook=json_load_object_hook)
            return self.stored_type(**json_loaded)

    def get_all_ids(self):
        return [name.stem for name in self.path.glob(self.FILENAME_TEMPLATE.format(id='*'))]

    def check_if_exist(self, id):
        filepath = self._build_filepath(id)
        return filepath.exists()

    def _build_filepath(self, id):
        return self.path / self.FILENAME_TEMPLATE.format(id=id)
