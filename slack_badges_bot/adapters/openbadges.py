import json
from slack_badges_bot.entities import Badge, Award, Issuer

class OpenBadges:
    """
    Esta clase sabe convertir entidades en objetos de OpenBadges con esquema JSON
    https://github.com/mozilla/openbadges-specification/blob/master/Assertion/latest.md
    """
    def __init__(self, config):
        self.config = config


    #https://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/examples/index.html
    def badge_assertion(self, award: Award):
        """
        Convierte una entidad badge en un esquema Badge Assertion
        #https://github.com/mozilla/openbadges-specification/blob/master/Assertion/latest.md#badgeassertion
        #TODO: IdentityHash para no mostrar email personal
        #http://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/history/1.1-specification.html#identityHash
        """
        return {
                "uid": award.id_str,
                "recipient":{
                    "type": "email",
                    "hashed": False,
                    "identity": award.person.email
                    },
                "badge": self.config['BADGES_JSON_URL'].format(award.badge.id_str),
                "verify": {
                    "type": "hosted",
                    "url": self.config['AWARDS_JSON_URL'].format(award.id_str)
                    },
                "issuedOn": award.timestamp,
                "image": self.config['AWARDS_IMAGE_URL'].format(award.id_str)
                }

    def issuer_organization(self, issuer: Issuer):
        return {
                "name": issuer.name,
                "url": issuer.url,
                "description": issuer.description
                }

    def badge_class(self, badge: Badge):
        return {
                "name": badge.name,
                "description": badge.description,
                "criteria": self.config['BADGES_CRITERIA_URL'].format(badge.id_str),
                "image": self.config['BADGES_IMAGE_URL'].format(badge.id_str),
                "issuer": self.config['ISSUER_URL']
                }



