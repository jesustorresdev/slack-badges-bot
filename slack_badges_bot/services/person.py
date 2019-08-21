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

#TODO: Corregir este nombre en todos lados
    def person_byemail(self, email):
        ids = self.retrieve_ids()
        email = email.lower().replace(" ", "")
        for id in ids:
            person = self.retrieve(id)
            if email == person.email:
                return person
        return None

    def byemail(self, email):
        return self.person_byemail(email)

    def byslack_id(self, slack_id):
        for person_id in self.retrieve_ids():
            person = self.retrieve(person_id)
            if person.slack_id == slack_id:
                return person
        return None

    def create_person(self, *, slack_name: str, slack_id: str, real_name: str, email: str):
        if self.person_byemail(email):
            raise ValueError(f'{email} ya existe!')
        person = Person(id=EntityID.generate_unique_id(),
                        slack_name=slack_name,
                        slack_id=slack_id,
                        real_name=real_name,
                        email=email)
        self.repository.save(person)
        return person

    def update_permissions(self, person, permissions, action):
        assert action in ['set', 'add', 'remove']
        assert isinstance(permissions, list), "permissions is not a list!"
        self.valid_permissions(permissions)
        if action == 'set':
            person.permissions = permissions
        elif action == 'add':
            for permission in permissions:
                if permission not in person.permissions:
                    person.permissions.append(permission)
        if action == 'remove':
            for permission in permissions:
                if permission in person.permissions:
                    person.permissions.remove(permission)
        self.repository.save(person, overwrite=True)


    def valid_permissions(self, permissions):
        # Comprobar si lo que hay en permissions está en ALL_PERMISSIONS
        for permission in permissions:
            if permission not in self.config['ALL_PERMISSIONS']:
                raise ValueError(f'{permission} is not one of {self.config["ALL_PERMISSIONS"]}')
        return all(permission in self.config['ALL_PERMISSIONS'] for permission in permissions)

    def has_permission(self, person, permission):
        return (permission in person.permissions)

