"""Servicios para gestionar las insignias (badges).
"""
from slack_badges_bot.entities import EntityID, Badge
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from pathlib import Path
from typing import List

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class BadgeService:
    def __init__(self, entity_repository_factory: EntityRepositoryFactory):
        self.badge_repository = entity_repository_factory(Badge)

    def create(self, name: str, description: str,
                criteria: List[str], image: Path):
        assert isinstance(image, Path)
        badge = Badge(id=EntityID.generate_unique_id(), name=name, description=description, criteria=criteria,
                      image=image)
# Poner id del badge en el png de la imagen
        badge.image.rename(badge.image.parent / f'{badge.id.hex}.png')
        badge.image = badge.image.parent/f'{badge.id.hex}.png'
        self.badge_repository.save(badge)

    def retrieve(self, id):
        return self.badge_repository.load(id)

    def retrieve_ids(self):
        return self.badge_repository.get_all_ids()

    def check_if_exist(self, id):
        return self.badge_repository.check_if_exist(id)

    def exists(self, badge_name):
        ids = self.retrieve_ids()
        for id in ids:
            badge = self.retrieve(id)
            a = badge.name.lower().replace(" ", "")
            b = badge_name.lower().replace(" ", "")
            if a == b:
                return True
        return False
