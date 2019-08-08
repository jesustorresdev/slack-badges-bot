"""Servicios para gestionar las insignias (badges).
"""
import inspect
import logging

from slack_badges_bot.entities import EntityID, Badge, BadgeImage
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from pathlib import Path
from typing import List, Union
from io import BufferedIOBase, BytesIO
from PIL import Image
from errors import *

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "apache license, version 2.0"
__copyright__ = "copyright 2019 {0} <{1}>".format(__author__, __contact__)


class BadgeService:
    def __init__(self, entity_repository_factory: EntityRepositoryFactory):
        self.badge_repository = entity_repository_factory(Badge)

    def create(self, name: str, description: str,
                criteria: List[str], image: BytesIO):
        logging.debug(f'LLAMADA a BadgeService.create({name})')
        image = BadgeImage(path=None, data=image)
        badge = Badge(id=EntityID.generate_unique_id(), name=name, description=description, criteria=criteria,
                      image=image)
        logging.debug(f'CREADO: {badge}')
        self.badge_repository.save(badge)
        logging.debug(f'GUARDADO: {badge}')

    def retrieve(self, id):
        return self.badge_repository.load(id)

    def retrieve_ids(self):
        all_ids = self.badge_repository.get_all_ids()
        logging.debug(all_ids)
        return all_ids

    def check_if_exist(self, id):
        return self.badge_repository.check_if_exist(id)

    def name_exists(self, badge_name):
        logging.debug(f'Comprobando si existe nombre {badge_name}')

        ids = self.retrieve_ids()
        badge_name = badge_name.lower().replace(" ", "")
        for id in ids:
            badge = self.retrieve(id)
            retrieved_badge_name = badge.name.lower().replace(" ", "")
            if badge_name == retrieved_badge_name:
                logging.debug(f'{badge_name} existe!')
                return True
        logging.debug(f'{badge_name} no existe')
        return False

    def open_image(self, badge: Badge) -> BufferedIOBase:
        '''
        Método para acceder a la imagen de una medalla
        '''
        if isinstance(badge.image, str):
            if Path(badge.image).exists:
                badge.image = BadgeImage(path=badge.image, data=None)
            else:
                raise ValueError(f'BadgeService.open_image: path {badge.image} doesn\'t exist')
        if isinstance(badge.image, BadgeImage):
            return badge.image.get_data()
        raise TypeError(f'BadgeService.open_image: Can\'t open image of type {type(badge.image)}')

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
