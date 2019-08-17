#encoding: utf-8
from slack_badges_bot.services.config import ConfigService
"""
Esta clase está pensada
para enviar mensajes de slack
con un formato bonito.
"""

class BlockBuilder:
    def __init__(self, config: ConfigService):
        self.config = config


    def award_block(self, award):
        user = award.person.slack_name
        badge = award.badge.name
        return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Nueva medalla para {user}*\n¡Felicidades {user}! has recibido {badge}"
                        }
                    },
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": f"{badge}",
                        "emoji": True
                        },
                    "image_url": self.config['AWARDS_IMAGE_URL'].format(award.id_str),
                    "alt_text": f"{badge}"
                    }
                ]

    def badges_block(self, badges):
        s = 's' if len(badges) is not 1 else ''
        colon = ':' if len(badges) > 0 else '.'
        block = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"En total hay *{len(badges)}* medalla{s}{colon}"
                            }
                    }
                ]
        for badge in badges:
            image_url = self.config['BADGES_IMAGE_URL'].format(badge.id_str)
            badge_block = self._badge_block(name=badge.name,
                                           description=badge.description,
                                           criteria=badge.criteria,
                                           image_url=image_url)
            for element in badge_block:
                block.append(element)
        return block

    def _badge_block(self, name, description, criteria, image_url):
        name = f":medal: {name} :medal:"
        description = f"_{description}_"
        criteria = "\n".join([":point_right:" + criterion for criterion in criteria])
        return [
                {
                    "type": "divider"
                    },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{name}\n{description}\n{criteria}\n"
                        },
                    "accessory": {
                        "type": "image",
                        "image_url": f"{image_url}",
                        "alt_text": f"{name}"
                        }
                    }
                ]

    def help_block(self, info):
        return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": info
                        }
                    }
                ]

    def award_list(self, awards, slack_username):
        s = 's' if len(awards) is not 1 else ''
        colon = ':' if len(awards) is not 0 else '.'
        block = [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{slack_username} tiene *{len(awards)}* medalla{s}{colon}"
                            }
                    }
                ]
        for award in awards:
            image_url = self.config['AWARDS_IMAGE_URL'].format(award.id_str)
            badge_block = self._badge_block(name=award.badge.name,
                                           description=award.badge.description,
                                           criteria=award.badge.criteria,
                                           image_url=image_url)
            for element in badge_block:
                block.append(element)
        return block
