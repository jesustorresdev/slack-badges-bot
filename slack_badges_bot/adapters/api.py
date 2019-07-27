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

from aiohttp import web
from apihelper import info
from pathlib import Path

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService
from slack_badges_bot.adapters.errors import *

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

    async def create_badge_handler(self, request):
        try:
            # Comprobando cabecera
            if request.headers['Content-Type'] != 'application/json':
                raise BadgeCreateError("Content-Type field of header must be application/json!")
            # Comprobar errores en los campos de request
            badge_json = await request.json()
            expected = set(["name", "description", "criteria", "image_data"])
            received = set([key for key in badge_json])
            if expected != received:
                raise BadgeCreateError("parameters missing!")
            if type(badge_json["name"]) is not str:
                raise BadgeCreateError("Name must be a string!")
            if len(badge_json["name"]) < self.config["BADGE_NAME_MIN_LENGTH"]:
                raise BadgeCreateError("Name must have more characters!")
            if self.badge_service.name_exists(badge_json["name"]):
                raise BadgeCreateError("Badge already exists!")
            if type(badge_json["description"]) is not str:
                raise BadgeCreateError("Description must be a string!")
            if len(badge_json["description"]) <  self.config['BADGE_DESCRIPTION_MIN_LENGTH']:
                raise BadgeCreateError("Description must have more characters!")
            if len(badge_json["criteria"]) < self.config['BADGE_MIN_CRITERIA']:
                raise BadgeCreateError("You must supply more criteria!")
            # Comprobar errores en la imagen
            image_id = uuid.uuid4().hex
            image_path = f"../data/badges/{image_id}.png"
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(badge_json['image_data']))
            with open(image_path, 'rb') as f:
                if imghdr.what(f) != 'png':
                    os.remove(image_path)
                    raise BadgeCreateError("Image is not a PNG!")
            # Procesar la imagen y guardarla para pasar un Path
            self.badge_service.create(name=badge_json['name'], description=badge_json['description'],
                                      criteria=badge_json['criteria'], image=Path(image_path))
            return web.Response(text=json.dumps({'status': 'success'}), status=200)
        except Exception as error:
            traceback.print_exc(file=sys.stdout)
            return web.Response(text=f"Bad Request: {str(error)}", status=400)

    def _setup_routes(self):
        self.app.router.add_post('/badges/create', self.create_badge_handler)
