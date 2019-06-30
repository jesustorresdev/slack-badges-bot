"""Aplicación de Slack
"""
import json

from aiohttp import web

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class SlackApplication:

    def __init__(self, config: ConfigService, badge_service: BadgeService):
        self.config = config
        self.badge_service = badge_service
        self.app = web.Application()
        self._setup_routes()

    async def slash_command(self, request):
        # TODO: Comprobar argumentos en request y añadir manejo de errores y excepciones
        # TODO: Usar signed secrets para comprobar que quien hace la petición es Slack.
        #       Ver https://api.slack.com/docs/verifying-requests-from-slack
        message_text = request.query['text']
        message_words = message_text.split()

        # TODO: Esto puede ser una pesadilla de ifs anidados. Pensar en otra manera.
        if message_words[1] == "badges":
            if message_words[2] == "list":
                badges = self.badge_service.retrieve_ids()
                return web.Response(text=json.dumps(
                    # TODO: Ojo con el insignia en singular si solo hay una.
                    {
                        "response_type": "ephemeral",
                        'text': f'Actualmente hay disponibles {len(badges)} insignias.',
                        'attachments': [
                            {'text': badge_id for badge_id in badges}
                        ],
                    }), status=200)

    def _setup_routes(self):
        self.app.router.add_post('/slash-command', self.slash_command)
