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
import mimetypes

from aiohttp import web
from aiohttp import ClientSession
from pathlib import Path
from io import BytesIO


from slack_badges_bot.entities import Badge, Award, Issuer
from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService
from slack_badges_bot.adapters.openbadges import OpenBadges
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
        self.openbadges = OpenBadges(config)
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
            response = web.json_response({'status': 'bad request', 'error': str(error)}, status=400)
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

    async def badge_handler(self, request):
        try:
            badge_id = request.match_info['badge_id']
            requested_data = request.match_info['requested_data']
            badge = self.badge_service.retrieve(badge_id, Badge)
            if requested_data == 'image':
                image_fd = self.badge_service.open_image(badge)
                content_type = mimetypes.guess_type(f'file.{badge.image.suffix}')[0]
                response = web.Response(body=image_fd.read(), content_type=content_type)
            elif requested_data == 'json':
                badge_class = self.openbadges.badge_class(badge)
                response = web.json_response(badge_class)
            elif requested_data == 'criteria':
                response = web.json_response({'criteria': badge.criteria})
            else:
                response = web.HTTPBadRequest()
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.HTTPInternalServerError()
        return response

    async def issuer_handler(self, request):
# Este método devuelve el JSON con la info del issuer
        try:
            issuer = self.badge_service.retrieve('issuer', Issuer)
            issuer_organization = self.openbadges.issuer_organization(issuer)
            logging.debug(issuer_organization)
            response = web.json_response(issuer_organization)
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.HTTPInternalServerError()
        return response

    async def award_handler(self, request: web.Request):
        try:
            award_id = request.match_info['award_id']
            requested_data = request.match_info['requested_data']
            award = self.badge_service.retrieve(award_id, Award)
            logging.debug(award)
            if requested_data == 'json':
                badge_assertion = self.openbadges.badge_assertion(award)
                response = web.json_response(badge_assertion)
            elif requested_data == 'image':
                image_fd = self.badge_service.open_image(award)
                content_type = mimetypes.guess_type(f'file.{award.image.suffix}')[0]
                response = web.Response(body=image_fd.read(), content_type=content_type)
            else:
                response = web.HTTPBadRequest()
        except:
            traceback.print_exc(file=sys.stdout)
            response = web.HTTPInternalServerError()
        return response

    def _setup_routes(self):
        self.app.router.add_post('/badges/create', self.create_badge_handler)
        self.app.router.add_get('/badges/{badge_id}/{requested_data}', self.badge_handler)
        self.app.router.add_get('/issuer', self.issuer_handler)
        self.app.router.add_get('/awards/{award_id}/{requested_data}', self.award_handler)
        #TODO: self.app.router.add_get('/{entity}/{id}/{requested_data}', self.entity_handler)
