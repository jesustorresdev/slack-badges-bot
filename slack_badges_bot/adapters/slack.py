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
import asyncio

from aiohttp import web
from io import BytesIO
from asyncache import cached
from cachetools import TTLCache

from slack_badges_bot.utils import info

from slack_badges_bot.entities import Badge, Award, BadgeImage

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.award import AwardService
from slack_badges_bot.services.person import PersonService
from slack_badges_bot.services.config import ConfigService

from slack_badges_bot.utils.blockbuilder import BlockBuilder
from slack_badges_bot.utils.openbadges import OpenBadges

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

class SlackApplication:

    def __init__(self, config: ConfigService,
                       badge_service: BadgeService,
                       award_service: AwardService,
                       person_service: PersonService):
        self.config = config
        self.secret = self.config['SLACK_SIGNING_SECRET']
        self.badge_service = badge_service
        self.award_service = award_service
        self.person_service = person_service

        self.app = web.Application()
        self._setup_routes()
        self.blockbuilder = BlockBuilder(self.config)
        self.slackclient = slack.WebClient(token=self.config['SLACK_OAUTH_ACCESS_TOKEN'],
                                            run_async=True)
        self.openbadges = OpenBadges(config)
        self.errortext = 'Error! :cry:'
        self._setup_users()

    def _setup_users(self):
        person_list = []
# Obtener todas las personas
        for person_id in self.person_service.retrieve_ids():
            person_list.append(self.person_service.retrieve(person_id))

        loop = asyncio.get_event_loop()
        users_list = loop.run_until_complete(self.users_list())

        for member in users_list.get('members'):
            email = member.get('profile').get('email')
            if email:
                if not self.person_service.person_byemail(email):
                    person = self.person_service.create_person(slack_id=member.get('id'),
                                      slack_name=member.get('name'),
                                      real_name=member.get('profile').get('real_name'),
                                      email=email)
                    if member.get('is_owner') or member.get('is_admin'):
                        # Dar todos los permisos
                        permissions = self.config['ALL_PERMISSIONS']
                    else:
                        permissions = self.config['USER_PERMISSIONS']
                    self.person_service.set_permissions(person, permissions)

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
                response = await self.list_user_badges(text.replace('list','',1))
            elif text.startswith('give'):
                response = await self.give_badge(text.replace('give','',1))
            elif text.startswith('help'):
                response = self.help_info()
            else:
                response = web.Response(text="Ese comando no existe!")
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.Response(text=self.errortext)
        return response

    def list_all_badges(self):
        badge_ids = self.badge_service.retrieve_ids()
        badges = [self.badge_service.retrieve(badge_id) for badge_id in badge_ids]
        s = 's' if len(badges) > 1 else ''
        return web.json_response(\
                {
                    "response_type": "ephemeral",
                    "text": f"Actualmente hay disponible{s} {len(badges)} insignia{s}.",
                    "blocks": self.blockbuilder.badges_block(badges),
                },\
                status=200)

    async def list_user_badges(self, text):
        slack_username  = text
        slack_id = await self.slack_id(slack_username)
        slack_email = await self.slack_email(slack_id)
        awards = self.award_service.byemail(slack_email)
        return web.json_response(\
                {
                    "response_type": "ephemereal",
                    "blocks": self.blockbuilder.award_list(awards, slack_username)
                },\
                status=200)

    async def give_badge(self, text):
        '''
        Metodo para crear asociaciones
        medalla-persona. Genera excepciones en caso
        de que algún parámetro sea incorrecto
        '''
        slack_username, badge_name = text.strip().split(' ', 1)
        slack_id = await self.slack_id(slack_username)
        if not slack_id:
            raise ValueError(f'Nombre de usuario no encontrado {slack_username}')
        # Obtener email o devolver error
        email = await self.slack_email(slack_id)
        if not email:
            raise ValueError(f'Email de usuario no encontrado {slack_id}')

        # Crear asociación
        award = self.award_service.issue(slack_name=slack_username,
                                         slack_id=slack_id,
                                         email=email,
                                         badge_name=badge_name)
        # Responder
        return web.json_response(\
                {
                    "response_type": "in_channel",
                    "blocks": self.blockbuilder.award_block(award),
                },\
                status=200)


    #https://api.slack.com/methods/users.list
    async def slack_id(self, slack_username):
        slack_username = slack_username.replace('@', '').strip()
        users_list = await self.users_list()
        for member in users_list['members']:
            if member['name'] == slack_username:
                return member['id']
        raise ValueError(f'{slack_username} not found')

    @cached(TTLCache(maxsize=1, ttl=180))
    async def users_list(self):
        return await self.slackclient.users_list()

    #https://api.slack.com/methods/users.info
    async def slack_email(self, slack_id):
        users_info = await self.users_info(slack_id)
        return users_info['user']['profile']['email']

    @cached(TTLCache(maxsize=1, ttl=180))
    async def users_info(self, slack_id):
        return await self.slackclient.users_info(user=slack_id)

    def help_info(self):
        info = """
        Comandos:
            */badges list all*
                Muestra una lista de todas las medallas existentes.
            */badges give @usuario [medalla]*
                Dar una medalla a un usuario. La medalla se indica por su nombre, por ejemplo:
                /badges give @Martín Medalla de oro
            */badges list @usuario*
                Muestra una lista con las medallas que se le han dado a un usuario.
        """
        return web.json_response(\
                {
                    "response_type": "ephemereal",
                    "blocks": self.blockbuilder.help_block(info),
                },\
                status=200)

    def _setup_routes(self):
        self.app.router.add_post('/slash-command', self.slash_command_handler)
