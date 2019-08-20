import json
from slack_badges_bot.entities import Badge, Award

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
                "badge": self.config['BADGES_URL'].format(badge_id=award.badge.id_str, requested_data='json'),
                "verify": {
                    "type": "hosted",
                    "url": self.config['AWARDS_URL'].format(award_id=award.id_str, requested_data='json')
                    },
                "issuedOn": award.timestamp,
                "image": self.config['AWARDS_URL'].format(award_id=award.id_str, requested_data='image')
                }

    def issuer_organization(self):
        return {
                "name": self.config['OPENBADGES_ISSUER_NAME'],
                "url": self.config['ISSUER_URL'],
                "description": self.config['OPENBADGES_ISSUER_DESCRIPTION']
                }

    def badge_class(self, badge: Badge):
        return {
                "name": badge.name,
                "description": badge.description,
                "criteria": self.config['BADGES_URL'].format(badge_id=badge.id_str, requested_data='criteria'),
                "image": self.config['BADGES_URL'].format(badge_id=badge.id_str, requested_data='image'),
                "issuer": self.config['ISSUER_URL']
                }



