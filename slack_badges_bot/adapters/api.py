"""Servicio web de gestión de la aplicación.
"""
import json
import logging
import uuid
import imghdr
import base64
import binascii
import traceback
import sys
import os
import re
import inspect

from aiohttp import web
from aiohttp import ClientSession
from pathlib import Path
from io import BytesIO

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService
from errors import *
from aiohttp_validate import validate

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

class WebService:

    def __init__(self, config: ConfigService, badge_service: BadgeService):
        self.config = config
        self.badge_service = badge_service
        self.app = web.Application()
        self._setup_routes()
        print(inspect.getmro(WebService))

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
            await self.extra_validation(request_json)
            # Crear medalla
            self.badge_service.create(name=request_json['name'],
                                      description=request_json['description'],
                                      criteria=request_json['criteria'],
                                      image=self.validated_image_bytes)
            # Respuesta
            return web.Response(text=json.dumps(\
                    {'status': 'success'}),\
                    status=200)
        except Exception as error:
            traceback.print_exc(file=sys.stdout)
            return web.Response(text=json.dumps(\
                    {'status': 'bad request', 'error': f'{error}'}),\
                    status=400)

    async def extra_validation(self, request_json: dict):
        if self.badge_service.name_exists(request_json["name"]):
            raise BadgeCreateError("Badge already exists!")
        image = request_json['image']
        if self.isbase64(image):
            self.validated_image_bytes = self.b64tobytes(image)
        elif self.isurl(image):
            self.validated_image_bytes = await self.urltobytes(image)
        else:
            raise BadgeCreateError(f'image field has not a valid encoding!')

        if self.badge_service.validate_image(self.validated_image_bytes):
            return True

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

    async def badge_image_handler(self, request):
        try:
            badge_id = request.match_info['badge_id']
            badge = self.badge_service.retrieve(badge_id)
            image_fd = self.badge_service.open_image(badge)
            logging.debug(f'badge_image_handler: {image_bytes}')
            response = web.Response(body=image_fd.read(), content_type='application/image')
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.HTTPBadRequest()
        return response



    def _setup_routes(self):
        self.app.router.add_post('/badges/create', self.create_badge_handler)
        self.app.router.add_get('/badges/{badge_id}/image', self.badge_image_handler)
