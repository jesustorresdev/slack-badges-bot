"""Definición de las entidades de la aplicación.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from slack_badges_bot.entities.entityid import EntityID

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
    image: Path


@dataclass
class Award:
    id: EntityID
    timestamp: datetime
    person: Person
    badge: Badge
