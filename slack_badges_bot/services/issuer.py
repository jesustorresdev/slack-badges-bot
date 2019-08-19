from slack_badges_bot.services.entity import EntityService
from slack_badges_bot.services.repositories import EntityRepositoryFactory
from slack_badges_bot.entities import Issuer

class IssuerService(EntityService):
    def __init__(self, entity_repository_factory: EntityRepositoryFactory):
        self.repository = entity_repository_factory(Issuer)

