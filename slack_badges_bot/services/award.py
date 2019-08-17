import datetime
import openbadges_bakery
import logging
import json

from io import BytesIO

from slack_badges_bot.services.entity import EntityService
from slack_badges_bot.services.person import PersonService
from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService
from slack_badges_bot.entities import EntityID, Award, Person, Badge, BadgeImage
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from slack_badges_bot.utils.openbadges import OpenBadges

class AwardService(EntityService):
    def __init__(self, entity_repository_factory: EntityRepositoryFactory,
            person_service: PersonService,
            badge_service: BadgeService,
            config: ConfigService):
        self.repository = entity_repository_factory(Award)
        self.person_service = person_service
        self.badge_service = badge_service
        self.openbadges = OpenBadges(config)

    def create_award(self, slack_name: str, slack_id: str,
                        email: str, badge_name: str):
        """
        Crea una asociación medalla-persona con la imagen de la medalla [badge_name]
        """
        if self.award_byemailandname(email, badge_name):
            raise ValueError(f'{email} ya tiene {badge_name}!')
        person = self.person_service.person_byemail(email)
        if not person:
            person = self.person_service.create_person(slack_name, slack_id, email)
        badge = self.badge_service.badge_byname(badge_name)
        if not badge:
            raise ValueError('badge name doesn\'t exist!')
        timestamp = datetime.datetime.utcnow().isoformat()
        award = Award(id=EntityID.generate_unique_id(),
                        timestamp=timestamp,
                        person=person,
                        badge=badge,
                        image=badge.image)
        self.repository.save(award)
        return award

    def award_byemailandname(self, email, badge_name):
        ids = self.retrieve_ids()
        badge = self.badge_service.badge_byname(badge_name)
        if not badge:
            return None
        for award in [self.retrieve(award_id) for award_id in ids]:
            if award.person.email == email\
                and award.badge.name == badge.name:
                return award
        return None

    def byemail(self, email):
        award_list = []
        ids = self.retrieve_ids()
        for award in [self.retrieve(award_id) for award_id in ids]:
            if award.person.email == email:
                award_list.append(award)
        return award_list

    #https://github.com/mozilla/openbadges-specification/blob/master/Assertion/latest.md
    def issue(self, slack_name: str, slack_id: str,
                         email: str, badge_name: str):
        award = self.create_award(slack_name=slack_name,
                                  slack_id=slack_id,
                                  email=email,
                                  badge_name=badge_name)
        award.image = self.bakery(award)
        self.repository.save(award, overwrite=True)
        return award

    #https://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/baking/index.html#baking
    def bakery(self, award: Award):
        assertion = self.openbadges.badge_assertion(award)
        image = self.badge_service.open_image(award)
        image = openbadges_bakery.bake(image, json.dumps(assertion))
        image.seek(0)
        image_bytes = BytesIO(image.read())
        return BadgeImage(data=image_bytes, path=None)
