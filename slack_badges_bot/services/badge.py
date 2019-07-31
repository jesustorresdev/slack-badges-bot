"""Servicios para gestionar las insignias (badges).
"""
import inspect

from slack_badges_bot.entities import EntityID, Badge
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from pathlib import Path
from typing import List
from io import BytesIO

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class BadgeService:
    def __init__(self, entity_repository_factory: EntityRepositoryFactory):
        self.badge_repository = entity_repository_factory(Badge)

    def create(self, name: str, description: str,
                criteria: List[str], image: BytesIO):
        print(f'Llamando a BadgeService.create({name})')
        print(f'Llamado desde {inspect.stack()[1].filename}')
        print(f'Llamado desde {inspect.stack()[1].lineno}')
        print(f'Llamado desde {inspect.stack()[1].function}')
        print(f'Llamado desde {inspect.stack()[1].code_context}')
        badge = Badge(id=EntityID.generate_unique_id(), name=name, description=description, criteria=criteria,
                      image=image)
        print(f'creado: {badge} con imagen {type(badge.image)}')
# Poner id del badge en el png de la imagen
        #badge.image.rename(badge.image.parent / f'{badge.id.hex}.png')
        #badge.image = badge.image.parent/f'{badge.id.hex}.png'
        self.badge_repository.save(badge)
        print(f'guardado: {badge} con imagen {type(badge.image)}')

    def retrieve(self, id):
        return self.badge_repository.load(id)

    def retrieve_ids(self):
        return self.badge_repository.get_all_ids()

    def check_if_exist(self, id):
        return self.badge_repository.check_if_exist(id)

    def name_exists(self, badge_name):
        print(f'comprobando si existe nombre {badge_name}')
        print(f'Llamado desde {inspect.stack()[1].filename}')
        print(f'Llamado desde {inspect.stack()[1].lineno}')
        print(f'Llamado desde {inspect.stack()[1].function}')
        print(f'Llamado desde {inspect.stack()[1].code_context}')

        ids = self.retrieve_ids()
        badge_name = badge_name.lower().replace(" ", "")
        for id in ids:
            badge = self.retrieve(id)
            retrieved_badge_name = badge.name.lower().replace(" ", "")
            if badge_name == retrieved_badge_name:
                print(f'{badge_name} existe!')
                return True
        print(f'{badge_name} no existe')
        return False
