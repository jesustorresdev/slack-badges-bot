"""Servicio web de gestión de la aplicación.
"""
import json

from aiohttp import web

from slack_badges_bot.services.badge import BadgeService
from slack_badges_bot.services.config import ConfigService

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

    async def create_badge(self, request):
        # TODO: Comprobar argumentos en request y añadir manejo de errores y excepciones
        self.badge_service.create(name=request.query['name'], description=request.query['description'],
                                  criteria=request.query['criteria'], image=request.query['image'])
        return web.Response(text=json.dumps({'status': 'success'}), status=200)

    def _setup_routes(self):
        self.app.router.add_post('/badges/create', self.create_badge)
