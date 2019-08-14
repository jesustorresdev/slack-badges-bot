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
    slack_name: str

    @property
    def id_str(self):
        return str(self.id.hex)

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

    @property
    def id_str(self):
        return str(self.id.hex)

@dataclass
class Award:
    id: EntityID
    timestamp: datetime
    person: Person
    badge: Badge
    image: Union[BadgeImage, str]

    def __post_init__(self):
        if type(self.person) is dict:
            self.person = Person(**self.person)
        if type(self.badge) is dict:
            self.badge = Badge(**self.badge)

    @property
    def id_str(self):
        return str(self.id.hex)

@dataclass
class Issuer:
    id: EntityID
    name: str
    url: str
    description: str


if __name__ == '__main__': # Probando
    pass
