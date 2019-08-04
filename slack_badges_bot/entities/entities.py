"""Definición de las entidades de la aplicación.
"""
import inspect
import logging

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Union
from io import BufferedIOBase

from slack_badges_bot.entities.entityid import EntityID
from slack_badges_bot.entities.badgeimage import BadgeImage

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

@dataclass
class Person:
    id: EntityID
    email: str
    slack_id: str

@dataclass
class Badge:
    """Clase para representar medallas
    Attributes:
        id (EntityID): identificador único.
        name (str): nombre de la medalla.
        description (str): descripción de la medalla.
        criteria (str): criterios para ganar la medalla.
        image (BadgeImage, str): imagen de la medalla.
            puede ser un string con la ruta del archivo o
            una instancia de la clase BadgeImage.
    """
    id: EntityID
    name: str
    description: str
    criteria: List[str]
    image: Union[BadgeImage, str]
    #_image: Image = field(init=False, repr=False)
    # problema: dataclasses.asdict() serializa también _image en el json
    # consecuencia: en el load intenta inicializar un atributo _image con init=False

    def __post_init__(self):
        logging.debug(f'Badge creado: {self}')

@dataclass
class Award:
    id: EntityID
    timestamp: datetime
    person: Person
    badge: Badge


def json_default(o):
    if isinstance(o, BufferedReader):
        o = None

if __name__ == '__main__': # Probando
    logging.basicConfig(level=logging.DEBUG)
    b = Badge(id=EntityID.generate_unique_id(),\
            name='Prueba', description='desc',\
            criteria=[], image='/tmp/prueba.png')#open('/tmp/prueba.png', 'rb'))
    print(b.asdict_factory())
