import logging

from slack_badges_bot.services.entity import EntityService
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from slack_badges_bot.entities import Person

class PersonService(EntityService):
    def __init__(self, entity_repository_factory: EntityRepositoryFactory):
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
