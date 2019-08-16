"""Servicios para gestionar las insignias (badges).
"""
import logging

from slack_badges_bot.entities import EntityID, Badge, BadgeImage
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from slack_badges_bot.services.entity import EntityService
from pathlib import Path
from typing import List, Union
from PIL import Image
from errors import *
from io import BytesIO

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "apache license, version 2.0"
__copyright__ = "copyright 2019 {0} <{1}>".format(__author__, __contact__)


class BadgeService(EntityService):
    def __init__(self, entity_repository_factory: EntityRepositoryFactory):
        self.repository = entity_repository_factory(Badge)

    def create_badge(self, name: str, description: str,
                criteria: List[str], image: BytesIO):
        if self.badge_byname(name):
            raise BadgeCreateError("Badge already exists!")
        if not self.validate_image(image):
            raise BadgeCreateError('La imagen de la medall no cumple los requisitos!')
        image = BadgeImage(path=None, data=image)
        badge = Badge(id=EntityID.generate_unique_id(), name=name, description=description, criteria=criteria,
                      image=image)
        self.repository.save(badge)
        return badge

    def badge_byname(self, badge_name):
        ids = self.retrieve_ids()
        badge_name = badge_name.lower().replace(" ", "")
        for id in ids:
            badge = self.retrieve(id)
            if badge_name == badge.name.lower().replace(" ", ""):
                return badge
        return None


    def validate_image(self, image_bytes: BytesIO) -> bool:
        #https://openbadges.org/developers/#badge-images
        assert isinstance(image_bytes, BytesIO),\
            'BadgeService.validate_image: image is not an instance of BytesIO'
        image = Image.open(image_bytes)
        if str(image.format).lower() not in ['png', 'svg']:
            raise BadgeImageError(f'Image must be png or svg ({image.format})')
        width, height = image.size
        if width != height: #images should be square
            raise BadgeImageError(f'Image must be squared ({width}x{height} px)')
        if image_bytes.getbuffer().nbytes > 256*1024: #not exceed 256kb
            raise BadgeImageError(f'Image must be 256kb or less ({image_bytes.nbytes}kb)')
        if width < 90: #not smaller than 90 x 90px
            raise BadgeImageError(f'Image must be bigger than 90 x 90 px ({width}x{height} px)')
        return True
