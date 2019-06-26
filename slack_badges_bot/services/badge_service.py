"""Servicios para gestionar las insignias (badges)
"""
from slack_badges_bot.entities import EntityID, Badge
from slack_badges_bot.ports.entity_repository import EntityRepositoryPort

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class BadgeService:

    def __init__(self, badge_repository: EntityRepositoryPort):
        self.badge_repository = badge_repository

    def create(self, name, description, criteria, image):
        badge = Badge(id=EntityID.generate_unique_id(), name=name, description=description, criteria=criteria,
                      image=image)
        self.badge_repository.save(badge)

    def retrieve(self, id):
        return self.badge_repository.load(id)

    def retrieve_ids(self):
        return self.badge_repository.get_all_ids()

    def check_if_exist(self, id):
        return self.badge_repository.check_if_exist(id)
