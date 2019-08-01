"""Servicios para gestionar las insignias (badges).
"""
import inspect
import logging

from slack_badges_bot.entities import EntityID, Badge
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from pathlib import Path
from typing import List, Union
from io import BytesIO
from PIL import Image
from errors import *

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class BadgeService:
    def __init__(self, entity_repository_factory: EntityRepositoryFactory):
        self.badge_repository = entity_repository_factory(Badge)

    def create(self, name: str, description: str,
                criteria: List[str], image: BytesIO):
        logging.debug(f'LLAMADA a BadgeService.create({name})')
        image_type = self.image_type(image)
        badge = Badge(id=EntityID.generate_unique_id(), name=name, description=description, criteria=criteria,
                      image=image, image_type=image_type)
        logging.debug(f'CREADO: {badge}')
        self.badge_repository.save(badge)
        logging.debug(f'GUARDADO: {badge}')

    def retrieve(self, id):
        return self.badge_repository.load(id)

    def retrieve_ids(self):
        return self.badge_repository.get_all_ids()

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

    def open_image(self, image: Union[str, BytesIO]) -> BytesIO:
        '''
        Método para leer la imagen. Si recibe un str abre la imagen,
        si recibe un BytesIO es que la imagen ya estaba abierta y lo devuelve
        '''
        fileformat = 'file://'
        if image.startswith(fileformat):
            image = image.replace(fileformat, '')
            with open(image, 'rb') as f:
                image_bytes = BytesIO(f.read())
        elif isinstance(image, BytesIO):
            image_bytes = image
        else:
            image_bytes = None
            raise TypeError(f'BadgeService.open_image: format not recognized')
        return image_bytes

    def image_type(self, image_bytes: BytesIO) -> str:
        assert isinstance(image_bytes, BytesIO),\
            'BadgeService.image_type: image is not an instance of BytesIO'
        return str(Image.open(image_bytes).format).lower()

    def validate_image(self, image_bytes: BytesIO) -> bool:
        #https://openbadges.org/developers/#badge-images
        assert isinstance(image_bytes, BytesIO),\
            'BadgeService.image_type: image is not an instance of BytesIO'
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
