"""Aplicación de Slack
"""
import json
import logging
import sys
import traceback
import urllib
import time
import hmac
import hashlib

from aiohttp import web

from slack_badges_bot.utils import info
from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService
from slack_badges_bot.adapters.blockbuilder import BlockBuilder

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
        self.blockbuilder = BlockBuilder(self.config)

    async def urlstring_to_json(self, request: web.Request):
        request_bytes = await request.read()
        request_json = urllib.parse.parse_qs(request_bytes.decode('utf-8'))
        request_json = {key:request_json[key][0] for key in request_json}
        return request_json

    async def verify_request(self, request: web.Request):
        #https://api.slack.com/docs/verifying-requests-from-slack
        slack_signature = request.headers['X-Slack-Signature']
        timestamp = request.headers['X-Slack-Request-Timestamp']
        secret = self.config['SLACK_SIGNING_SECRET']
        version_number = 'v0'
        req_body = await request.read()
        now = time.time()

        if abs(now - timestamp) > self.config['SLACK_VERIFY_SECONDS']:
            raise web.HTTPForbidden

        message = ':'.join([version_number, timestamp, req_body])
        request_signature = hmac.new(secret, msg=message, digestmod=haslib.sha256)

        if not hmac.compare_digest(slack_signature, request_signature):
            raise web.HTTPForbidden()

        return True

    async def slash_command_handler(self, request):
        # TODO: Comprobar argumentos en request y añadir manejo de errores y excepciones
        # TODO: Usar signed secrets para comprobar que quien hace la petición es Slack.
        #       Ver https://api.slack.com/docs/verifying-requests-from-slack
        try:
            # request.query['text'] produce "KeyError: 'text'"
            request_json = await self.urlstring_to_json(request)
            if request_json['command'] != '/badges':
                raise web.HTTPBadRequest

            text = request_json['text'].strip()
            if text.startswith('list all'):
                response = self.list_all_badges()
            elif text.startswith('list'):
                response = self.list_user_badges(text.replace('list','',1))
            elif text.startswith('give'):
                response = self.give_badge(text.replace('give','',1))
            elif text.startswith('help'):
                response = self.help_info()
            else:
                response = web.Response(text="Ese comando no existe!")
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.Response(text="Error! :cry:")
        return response

    def list_all_badges(self):
        badge_ids = self.badge_service.retrieve_ids()
        badges = [self.badge_service.retrieve(badge_id) for badge_id in badge_ids]
        logging.debug(badges)
        s = 's' if len(badges) > 1 else ''
        block = self.blockbuilder.badges_block(badges)
        logging.debug(block)
        logging.debug(json.dumps(block,indent=True))
        return web.json_response(\
                {
                    "response_type": "ephemeral",
                    "text": f"Actualmente hay disponible{s} {len(badges)} insignia{s}.",
                    "blocks": self.blockbuilder.badges_block(badges),
                },\
                status=200)

    def list_user_badges(self, text):
        raise NotImplementedError
    def give_badge(self, text):
        raise NotImplementedError
    def help_info(self):
        raise NotImplementedError

    def _setup_routes(self):
        self.app.router.add_post('/slash-command', self.slash_command_handler)
