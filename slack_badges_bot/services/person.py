import logging

from typing import List

from slack_badges_bot.services.entity import EntityService
from slack_badges_bot.services.config import ConfigService
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from slack_badges_bot.entities import Person, EntityID

class PersonService(EntityService):
    def __init__(self, config: ConfigService,
            entity_repository_factory: EntityRepositoryFactory):
        self.config = config
        self.repository = entity_repository_factory(Person)

    def person_byemail(self, email):
        ids = self.retrieve_ids()
        email = email.lower().replace(" ", "")
        for id in ids:
            person = self.retrieve(id)
            if email == person.email:
                return person
        return None

    def create_person(self, *, slack_name: str, slack_id: str, email: str):
        if self.person_byemail(email):
            raise ValueError(f'{email} ya existe!')
        person = Person(id=EntityID.generate_unique_id(),
                        slack_name=slack_name,
                        slack_id=slack_id,
                        email=email)
        self.repository.save(person)
        return person

    def set_permissions(self, person: Person, permissions: List[str]):
        assert isinstance(permissions, list), "permissions is not a list!"
        for permision in permissions:
            if permision not in self.config['PERSON_PERMISSIONS']:
                raise ValueError(f'Permision {permision} doesn\'t exist')
        person.permissions = permissions
        self.repository.save(person, overwrite=True)
