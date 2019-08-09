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
        self.secret = self.config['SLACK_SIGNING_SECRET']
        self.badge_service = badge_service
        self.app = web.Application()
        self._setup_routes()
        self.blockbuilder = BlockBuilder(self.config)

    async def verify_request(self, request: web.Request):
        #https://api.slack.com/docs/verifying-requests-from-slack
        slack_signature = request.headers['X-Slack-Signature'] #str
        timestamp = request.headers['X-Slack-Request-Timestamp'] #str
        version_number = 'v0' #str
        req_body = await request.read() #bytes
        secret = self.config['SLACK_SIGNING_SECRET'] #str
        now = time.time() # float

        if abs(now - float(timestamp)) > float(self.config['SLACK_VERIFY_SECONDS']):
            raise web.HTTPForbidden

        base_string = ':'.join([version_number, timestamp, req_body.decode('utf-8')]) # str
        base_string = str.encode(base_string) # bytes

        request_signature = 'v0=' +  hmac.new(
                                         str.encode(self.secret),
                                         base_string,
                                         hashlib.sha256
                                     ).hexdigest()

        if not hmac.compare_digest(slack_signature, request_signature):
            raise web.HTTPForbidden()

        return True

    async def slash_command_handler(self, request):
        try:
            await self.verify_request(request)

            request_post = await request.post()

            logging.debug(request_post)

            if request_post['command'] != '/badges':
                raise web.HTTPBadRequest

            text = request_post['text'].strip()
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
        s = 's' if len(badges) > 1 else ''
        block = self.blockbuilder.badges_block(badges)
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
