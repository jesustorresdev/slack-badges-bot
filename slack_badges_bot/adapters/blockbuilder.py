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


    def award_text_block(self, user_id, badge_name, award_png_url):
        return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Nueva medalla para {user_id}*\n¡Felicidades {user_id}! has recibido {badge_name}"
                        }
                    },
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": f"{badge_name}",
                        "emoji": True
                        },
                    "image_url": f"{award_png_url}",
                    "alt_text": f"{badge_name}"
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
