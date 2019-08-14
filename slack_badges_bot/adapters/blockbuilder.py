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
        block = []
        for badge in badges:
            image_url = self.config["BADGES_URL"] + f"/{badge.id_str}/image"
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
