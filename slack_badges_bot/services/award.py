import datetime

from slack_badges_bot.services.entity import EntityService
from slack_badges_bot.services.person import PersonService
from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.entities import EntityID, Award, Person, Badge
from slack_badges_bot.services.repositories import EntityRepositoryFactory

class AwardService(EntityService):
    def __init__(self, entity_repository_factory: EntityRepositoryFactory):
        self.repository = entity_repository_factory(Award)
        self.person_service = PersonService(entity_repository_factory)
        self.badge_service = BadgeService(entity_repository_factory)

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
        for award_id in ids:
            award = self.retrieve(award_id)
            if award.person.email == email\
                and award.badge.name == badge.name:
                return award
        return None
