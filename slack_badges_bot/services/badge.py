"""Servicios para gestionar las insignias (badges).
"""
import inspect
import logging
import datetime

from slack_badges_bot.entities import EntityID, Badge, BadgeImage, Award, Person, Issuer
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
        self.person_repository = entity_repository_factory(Person)
        self.award_repository = entity_repository_factory(Award)
        self.issuer_repository = entity_repository_factory(Issuer)

    def create_badge(self, name: str, description: str,
                criteria: List[str], image: BytesIO):
        if self.badge_byname(name):
            raise BadgeCreateError("Badge already exists!")
        if not self.validate_image(image):
            raise BadgeCreateError('La imagen de la medall no cumple los requisitos!')
        image = BadgeImage(path=None, data=image)
        badge = Badge(id=EntityID.generate_unique_id(), name=name, description=description, criteria=criteria,
                      image=image)
        self.badge_repository.save(badge)
        return badge

    def create_person(self, slack_name: str, slack_id: str, email: str):
        if self.person_byemail(email):
            raise ValueError(f'{email} ya existe!')
        person = Person(id=EntityID.generate_unique_id(),
                        slack_name=slack_name,
                        slack_id=slack_id,
                        email=email)
        self.person_repository.save(person)
        return person

    def create_award(self, slack_name: str, slack_id: str,
                        email: str, badge_name: str):
        """
        Crea una asociación medalla-persona con la imagen de la medalla [badge_name]
        """
        if self.award_byemailandname(email, badge_name):
            raise ValueError(f'{email} ya tiene {badge_name}!')
        person = self.person_byemail(email)
        if not person:
            person = self.create_person(slack_name, slack_id, email)
        badge = self.badge_byname(badge_name)
        if not badge:
            raise ValueError('badge name doesn\'t exist!')
        timestamp = datetime.datetime.utcnow().isoformat()
        award = Award(id=EntityID.generate_unique_id(),
                        timestamp=timestamp,
                        person=person,
                        badge=badge,
                        image=badge.image)
        self.award_repository.save(award)
        return award

    def retrieve(self, id, entity: Union[Award, Person, Badge]):
        repository = getattr(self, f'{entity.__name__.lower()}_repository')
        if repository:
            return repository.load(id)
        else:
            raise ValueError(f'unknown class! {entity}')

    def retrieve_ids(self, entity: Union[Award, Person, Badge]):
        repository = getattr(self, f'{entity.__name__.lower()}_repository')
        if repository:
            return repository.get_all_ids()
        else:
            raise ValueError(f'unknown class! {entity}')

    def badge_byname(self, badge_name):
        ids = self.retrieve_ids(Badge)
        badge_name = badge_name.lower().replace(" ", "")
        for id in ids:
            badge = self.retrieve(id, Badge)
            retrieved_badge_name = badge.name.lower().replace(" ", "")
            if badge_name == retrieved_badge_name:
                return badge
        return None

    def person_byemail(self, email):
        ids = self.retrieve_ids(Person)
        email = email.lower().replace(" ", "")
        for id in ids:
            person = self.retrieve(id, Person)
            if email == person.email:
                return person
        return None

    def award_byemailandname(self, email, badge_name):
        ids = self.retrieve_ids(Award)
        badge = self.badge_byname(badge_name)
        for award_id in ids:
            award = self.retrieve(award_id, Award)
            if award.person.email == email\
                and award.badge.name == badge.name:
                return award
        return None

    def open_image(self, badge: Badge) -> BufferedIOBase:
        '''
        Sustituye el atributo image de Badge por un
        BadgeImage si no lo es y devuelve un descriptor
        del fichero de la imagen
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
