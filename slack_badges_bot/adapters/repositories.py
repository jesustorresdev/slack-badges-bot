"""Repositorios para la persistencia de datos.
"""
import json
import dataclasses
import uuid
import logging
import inspect

from pathlib import Path
from typing import Type
from io import BytesIO

from slack_badges_bot.services.repositories import EntityRepository
from slack_badges_bot.entities.entities import Badge

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

def json_dump_default(o):
    """Función para pasar por el argumento default a la función json.dump().

    Añade soporte para atributos UUID en la codificación a JSON. Estos atributos se codifican en formato URN para
    facilitar su identificación posterior a la hora de decodificarlos.

    Añade soporte para atributos de tipo Path pasándolos a un string.
    """
    if isinstance(o, uuid.UUID):
        return o.urn
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f'Unknown type of object {o}')

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
    FILENAME_TEMPLATE = '{id}.{filetype}'

    def __init__(self, stored_type: Type, path: Path):
        self._stored_type = stored_type
        self.path = path

    @property
    def stored_type(self):
        return self._stored_type

    def save(self, entity, overwrite=False):
        if isinstance(entity, Badge):
            if isinstance(entity.image, BytesIO):
                logging.debug(f'EntityJSONRepository.save: {entity.image}')
                image_filepath = self._build_filepath(entity.id.hex, entity.image_type)
                with image_filepath.open('wb') as f:
                    entity.image.seek(0)
                    f.write(entity.image.read())
                entity.image = 'file://' + str(image_filepath)
        filepath = self._build_filepath(entity.id.hex, 'json')
        mode = "w" if overwrite else "x"
        with filepath.open(mode) as f:
            json.dump(dataclasses.asdict(entity), f, default=json_dump_default)

    def load(self, id):
        logging.debug(f'EntityJSONRepository.load({id})')
        filepath = self._build_filepath(id, 'json')
        with filepath.open("r") as f:
            json_loaded = json.load(f, object_hook=json_load_object_hook)
            return self.stored_type(**json_loaded)

    def get_all_ids(self):
        return [name.stem for name in self.path.glob(self.FILENAME_TEMPLATE.format(id='*', filetype='json'))]

    def check_if_exist(self, id):
        filepath = self._build_filepath(id)
        return filepath.exists()

    def _build_filepath(self, id, filetype):
        return self.path / self.FILENAME_TEMPLATE.format(id=id, filetype=filetype)
