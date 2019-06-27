"""Servicio web de gestión de la aplicación.
"""
from aiohttp import web
import json

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

    async def start(self):
        # TODO: Estudiar si es conveniente que este runner maneje las señales del sistema
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host=self.config['HTTP_HOST'], port=self.config['HTTP_PORT'])
        await site.start()

        # site se ejecuta de forma ininterrumpida. Limpiar runner cuando site se detenga definitivamente.
        await runner.cleanup()

    def _setup_routes(self):
        self.app.router.add_post('/badges/create', self.create_badge)
