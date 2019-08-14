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
import slack
import openbadges_bakery
import time


from aiohttp import web
from io import BytesIO

from slack_badges_bot.utils import info

from slack_badges_bot.entities import Badge, Award, BadgeImage

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService

from slack_badges_bot.adapters.blockbuilder import BlockBuilder
from slack_badges_bot.adapters.openbadges import OpenBadges

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

class SlackApplication:

    def __init__(self, config: ConfigService,
                    badge_service: BadgeService):
        self.config = config
        self.secret = self.config['SLACK_SIGNING_SECRET']
        self.badge_service = badge_service
        self.app = web.Application()
        self._setup_routes()
        self.blockbuilder = BlockBuilder(self.config)
        self.errorresponse = web.Response(text='Error! :cry:')
        self.slackclient = slack.WebClient(token=self.config['SLACK_OAUTH_ACCESS_TOKEN'],
                                            run_async=True)
        self.openbadges = OpenBadges(config)
        self.users_list_time = 0
        self.users_info_time = 0

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

            if request_post['command'] != '/badges':
                raise web.HTTPBadRequest

            text = request_post['text'].strip()
            if text.startswith('list all'):
                response = self.list_all_badges()
            elif text.startswith('list'):
                response = self.list_user_badges(text.replace('list','',1))
            elif text.startswith('give'):
                response = await self.give_badge(text.replace('give','',1))
            elif text.startswith('help'):
                response = self.help_info()
            else:
                response = web.Response(text="Ese comando no existe!")
        except:
            traceback.print_exc(file=sys.stdout)
            response = self.errorresponse
        return response

    def list_all_badges(self):
        badge_ids = self.badge_service.retrieve_ids(Badge)
        badges = [self.badge_service.retrieve(badge_id, Badge) for badge_id in badge_ids]
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

    async def give_badge(self, text):
        '''
        Metodo para crear asociaciones
        medalla-persona. Genera excepciones en caso
        de que algún parámetro sea incorrecto
        '''
        slack_username, badge_name = text.strip().split(' ', 1)
        slack_id = await self.slack_id(slack_username.replace('@', ''))
        if not slack_id:
            raise ValueError(f'Nombre de usuario no encontrado {slack_username}')
        # Obtener email o devolver error
        email = await self.slack_email(slack_id)
        if not email:
            raise ValueError(f'Email de usuario no encontrado {slack_id}')

        # Crear asociación
        award = self.openbadges_award(slack_name=slack_username,
                                      slack_id=slack_id,
                                      email=email,
                                      badge_name=badge_name)
        # Responder
        return web.json_response(\
                {
                    "response_type": "in_channel",
                    "text": f"Felicidades!!!",
                    "blocks": self.blockbuilder.award_block(award),
                },\
                status=200)

    #https://github.com/mozilla/openbadges-specification/blob/master/Assertion/latest.md
    def openbadges_award(self, slack_name: str, slack_id: str,
                         email: str, badge_name: str):
        logging.debug(f'Creando openbadges award')
        award = self.badge_service.create_award(slack_name=slack_name,
                                                slack_id=slack_id,
                                                email=email,
                                                badge_name=badge_name)
        logging.debug(award)
        award.image = self.bakery(award)
        self.badge_service.award_repository.save(award, overwrite=True)
        logging.debug(award)

        return award

    #https://www.imsglobal.org/sites/default/files/Badges/OBv2p0Final/baking/index.html#baking
    def bakery(self, award: Award):
        assertion = self.openbadges.badge_assertion(award)
        image = self.badge_service.open_image(award)
        image = openbadges_bakery.bake(image, json.dumps(assertion))
        image.seek(0)
        image_bytes = BytesIO(image.read())
        return BadgeImage(data=image_bytes, path=None)

    #https://api.slack.com/methods/users.list
    async def slack_id(self, slack_username):
        # Actualizar cache cada 3 minutos
        if time.time() - self.users_list_time > 180:
            self.users_list = None
        if not self.users_list:
            self.users_list_time = time.time()
            self.users_list = await self.slackclient.users_list()
        for member in self.users_list['members']:
            if member['name'] == slack_username:
                return member['id']

    #https://api.slack.com/methods/users.info
    async def slack_email(self, slack_id):
        # Actualizar cache cada 3 minutos
        if time.time() - self.users_info_time > 180:
            self.users_info = None
        if not self.users_info:
            self.users_info_time = time.time()
            self.users_info = await self.slackclient.users_info(user=slack_id)
        return self.users_info['user']['profile']['email']

    def help_info(self):
        raise NotImplementedError

    def _setup_routes(self):
        self.app.router.add_post('/slash-command', self.slash_command_handler)
