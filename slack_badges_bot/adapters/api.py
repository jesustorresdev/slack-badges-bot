"""Servicio web de gestión de la aplicación.
"""
import json
import logging
import uuid
import imghdr
import base64
import traceback
import sys
import os
import re

from aiohttp import web
from pathlib import Path
from io import BytesIO

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService
from errors import *

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

    async def create_badge_handler(self, request: web.Request):
        try:
            request_json = await request.json()
            # Validar
            self.create_badge_validation(request.headers, request_json)
            # Decodificar imagen
            image = request_json['image']
            if self.validated_encoding == BASE64:
                image_bytes = self.b64tobytes(image)
            elif self.validated_encoding == URL:
                image_bytes = self.urltobytes(image)
            print(f'Request validada y el tipo de image es {self.validated_encoding}')
            # Crear medalla
            self.badge_service.create(name=request_json['name'], description=request_json['description'],
                                      criteria=request_json['criteria'], image=image_bytes)
            # Respuesta
            return web.Response(text=json.dumps({'status': 'success'}), status=200)
        except Exception as error:
            traceback.print_exc(file=sys.stdout)
            return web.Response(text=f"Bad Request: {str(error)}", status=400)

    def create_badge_validation(self, headers, request_json: dict):
        if headers['Content-Type'] != 'application/json':
            raise BadgeCreateError("Content-Type field of header must be application/json!")
        expected = set(["name", "description", "criteria", "image"])
        received = set([key for key in request_json])
        if expected != received:
            raise BadgeCreateError(f"parameters missing! Expected:{expected}, received: {received}")
        if type(request_json["name"]) is not str:
            raise BadgeCreateError("Name must be a string!")
        if len(request_json["name"]) < self.config["BADGE_NAME_MIN_LENGTH"]:
            raise BadgeCreateError("Name must have more characters!")
        if self.badge_service.name_exists(request_json["name"]):
            raise BadgeCreateError("Badge already exists!")
        if type(request_json["description"]) is not str:
            raise BadgeCreateError("Description must be a string!")
        if len(request_json["description"]) < self.config['BADGE_DESCRIPTION_MIN_LENGTH']:
            raise BadgeCreateError("Description must have more characters!")
        if len(request_json["criteria"]) < self.config['BADGE_MIN_CRITERIA']:
            raise BadgeCreateError("You must supply more criteria!")
        self.validated_encoding = self.image_encoding(request_json['image'])
        if self.validated_encoding is None:
            raise BadgeCreateError(f'Image has not a valid encoding!')
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
            base64.b64decode(data)
            return True
        except:
            return False

    def isurl(self, data: str):
        pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.match(pattern, data.strip())

    def b64tobytes(self, data: str):
        return BytesIO(base64.b64decode(data))

    def urltobytes(self, data: str):
        raise NotImplementedError

    def _setup_routes(self):
        self.app.router.add_post('/badges/create', self.create_badge_handler)
