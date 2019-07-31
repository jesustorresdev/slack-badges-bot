"""Definición de las entidades de la aplicación.
"""
import inspect

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List
from io import StringIO

from slack_badges_bot.entities.entityid import EntityID
from slack_badges_bot.entities.image import BadgeImage

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
    id: EntityID
    name: str
    description: str
    criteria: List[str]
#https://blog.florimond.dev/reconciling-dataclasses-and-properties-in-python
    image: BadgeImage # Llama al setter
    _image: BadgeImage = field(init = False, repr = False)

    @property
    def image(self):
        print(f'Badge.image.getter')
        print(f'Llamado desde {inspect.stack()[1].filename}')
        print(f'Llamado desde {inspect.stack()[1].lineno}')
        print(f'Llamado desde {inspect.stack()[1].function}')
        print(f'Llamado desde {inspect.stack()[1].code_context}')
        return self._image.get()

    @image.setter
    def image(self, value):
        print(f'Llamando a image.setter({value})')
        print(f'Llamado desde {inspect.stack()[1].filename}')
        print(f'Llamado desde {inspect.stack()[1].lineno}')
        print(f'Llamado desde {inspect.stack()[1].function}')
        print(f'Llamado desde {inspect.stack()[1].code_context}')
        self._image = BadgeImage(value)

    @property
    def image_type(self):
        self._image.get_type()

@dataclass
class Award:
    id: EntityID
    timestamp: datetime
    person: Person
    badge: Badge

#if __name__ == '__main__':
#    b = Badge(id=EntityID.generate_unique_id(), name="Pepe", description="Blabla", criteria=[], image="/tmp/prueba")
#    print(b.image)
