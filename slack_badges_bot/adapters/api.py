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


URL = 'url'
BASE64 = 'base64'

class WebService:

    def __init__(self, config: ConfigService, badge_service: BadgeService):
        self.config = config
        self.badge_service = badge_service
        self.app = web.Application()
        self._setup_routes()
        self.validated_encoding = None
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
            #request_json = await request.json()
            # Validar
            self.extra_validation(request_json)
            ## Crear medalla
            self.badge_service.create(name=request_json['name'], description=request_json['description'],
                                      criteria=request_json['criteria'], image=self.validated_image_bytes)
            # Respuesta
            return web.Response(text=json.dumps(\
                    {'status': 'success'}),\
                    status=200)
        except Exception as error:
            traceback.print_exc(file=sys.stdout)
            return web.Response(text=json.dumps(\
                    {'status': 'bad request', 'error': f'{str(error)}'}),\
                    status=400)

    def extra_validation(self, request_json: dict):
        if self.badge_service.name_exists(request_json["name"]):
            raise BadgeCreateError("Badge already exists!")
        self.validated_encoding = self.image_encoding(request_json['image'])
        if self.validated_encoding is None:
            raise BadgeCreateError(f'Image has not a valid encoding!')
        image = request_json['image']
        if self.validated_encoding == BASE64:
            self.validated_image_bytes = self.b64tobytes(image)
        elif self.validated_encoding == URL:
            self.validated_image_bytes = self.urltobytes(image)
        if self.badge_service.validate_image(self.validated_image_bytes):
            return True

    def image_encoding(self, image: str):
        assert isinstance(image, str), 'Not an instance of str'
        if self.isurl(image):
            return URL
        elif self.isbase64(image):
            return BASE64
        else:
            return None

    def isbase64(self, data: str):
        try:
            pattern = 'data:image\/[a-zA-Z]*;base64'
            prefix, data = data.split(',')
            if re.match(pattern, prefix):
                base64.b64decode(data)
                return True
            else:
                return False
        except binascii.Error:
            return False

    def isurl(self, data: str):
        pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.match(pattern, data.strip())

    def b64tobytes(self, data: str):
        return BytesIO(base64.b64decode(data.split(',')[-1]))

    def urltobytes(self, data: str):
        raise NotImplementedError

    def _setup_routes(self):
        self.app.router.add_post('/badges/create', self.create_badge_handler)
