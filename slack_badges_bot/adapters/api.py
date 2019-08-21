"""API para la línea de comandos
"""
import json
import base64
import binascii
import traceback
import sys
import re

from aiohttp import web
from aiohttp import ClientSession
from pathlib import Path
from io import BytesIO
from dataclasses import asdict


from slack_badges_bot.entities import Badge, Award, Person
from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService
from slack_badges_bot.services.person import PersonService
from errors import *
from aiohttp_validate import validate

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

class WebService:

    def __init__(self, config: ConfigService,
            badge_service: BadgeService,
            person_service: PersonService):
        self.config = config
        self.badge_service = badge_service
        self.person_service = person_service
        self.app = web.Application()
        self._setup_routes()

    @validate(
            request_schema = {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'minLenght': 5
                        },
                    'description':{
                        'type': 'string',
                        'minLength': 10
                        },
                    'criteria':{
                        'type': 'array',
                        'items': {
                            'type': 'string'
                            },
                        'minItems': 3
                        },
                    'image':{
                        'type': 'string'
                        }
                    },
                'required': ['name', 'description', 'criteria', 'image'],
                'aditionalProperties': False
                },
            response_schema = {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'error' : {'type': 'string'}
                    },
                'required': ['status']
                }
            )
    async def create_badge_handler(self, request_json, request):
        try:
            # Validar si existe nombre de medalla, tipo de imagen, etc.
            image_bytes = await self.get_image_bytes(request_json['image'])
            # Crear medalla
            self.badge_service.create_badge(name=request_json['name'],
                                      description=request_json['description'],
                                      criteria=request_json['criteria'],
                                      image=image_bytes)
            # Respuesta
            response = web.json_response({'status': 'success'}, status=200)
        except Exception as error:
            traceback.print_exc(file=sys.stdout)
            response = web.json_response({'status': 'error',
                                        'error': str(error)},
                                        status=500)
        return response

    async def get_image_bytes(self, image: str):
        if self.isbase64(image):
            return self.b64tobytes(image)
        elif self.isurl(image):
            return (await self.urltobytes(image))
        else:
            raise BadgeCreateError(f'image field has not a valid encoding!')

    def isbase64(self, data: str):
        try:
            pattern = 'data:image\/[a-zA-Z]*;base64[^-A-Za-z0-9+/=]|=[^=]|={3,}$'
            if re.match(pattern, data):
                prefix, data = data.split(',')
                base64.b64decode(data)
                return True
            else:
                return False
        except binascii.Error:
            return False

    def isurl(self, data: str):
        pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        if re.match(pattern, data.strip()):
            return True
        return False

    def b64tobytes(self, data: str):
        return BytesIO(base64.b64decode(data.split(',')[-1]))

    async def urltobytes(self, url: str):
        async with ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return BytesIO(await resp.read())
        raise BadgeImageError(f'WebService.urltobytes: couldn\'t dowload badge image from {url}')

    async def list_persons_handler(self, request):
        persons = self.person_service.retrieve_all()
        for person in persons:
            person.id = person.id_str
        return web.json_response([asdict(person) for person in persons])

    @validate(
            request_schema = {
                'type': 'object',
                'properties': {
                    'person_id': {
                        'type': 'string',
                        'minLenght': 5
                        },
                    'action': {
                        'type': 'string',
                        'enum': ['set', 'add', 'remove']
                        },
                    'permissions':{
                        'type': 'array',
                        'items': {
                            'type': 'string'
                            },
                        'minItems': 1
                        }
                    },
                'required': ['person_id', 'permissions'],
                'aditionalProperties': False
                },
            response_schema = {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'error' : {'type': 'string'}
                    },
                'required': ['status']
                }
            )
    async def update_permissions_handler(self, request_json, request):
        """
        Handler que recibe un POST con un json indicando el id de la persona
        y los nuevos permisos
        """
        try:
            person = self.person_service.retrieve(request_json['person_id'])
            self.person_service.update_permissions(person,
                    request_json['permissions'],
                    request_json['action'])
            response = web.json_response({'status':'ok'})
        except Exception as error:
            traceback.print_exc(file=sys.stdout)
            response = web.json_response({'status': 'error',
                    'error': str(error)}, status=500)
        return response

    async def list_permissions_handler(self, request):
        return web.json_response(self.config['ALL_PERMISSIONS'])

    def _setup_routes(self):
        self.app.router.add_post(self.config['ADMIN_BADGES_CREATE'],
                self.create_badge_handler)

        self.app.router.add_get(self.config['ADMIN_PERSONS_LIST'],
                self.list_persons_handler)

        self.app.router.add_post(self.config['ADMIN_PERMISSIONS_UPDATE'],
                self.update_permissions_handler)

        self.app.router.add_get(self.config['ADMIN_PERMISSIONS_LIST'],
                self.list_permissions_handler)
