"""Punto de entrada de la aplicación
"""
import punq
import os
import logging

from aiohttp import web
from pathlib import Path

from slack_badges_bot import adapters, entities, services

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

config = services.config.ConfigService()
config.from_object('slack_badges_bot.settings.DefaultConfig')

# Inyección de dependencias
a = adapters.repositories.EntityJsonRepository
container = punq.Container()
container.register(services.config.ConfigService, instance=config)
container.register(services.badge.BadgeService)

container.register(services.repositories.EntityRepositoryFactory)
container.register(services.repositories.EntityRepository, adapters.repositories.EntityJsonRepository,
                   stored_type=entities.Badge, path=config.option_as_path('DATA_PATH') / 'badges')
# TODO: registrar repositorios de awards, persons e issuer
# --> https://punq.readthedocs.io/en/latest/ ejemplo del Authenticator

def init_app(argv):
    if config['DEBUG']:
        # Activar el modo de depuración de asyncio.
        os.environ['PYTHONASYNCIODEBUG'] = "1"
        # Configurar el logger a nivel logging.DEBUG
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                datefmt='%Y-%m-%d:%H:%M:%S',
                level=logging.DEBUG)

    app = web.Application()
    app.add_subapp('/api', adapters.api.WebService(
        config=config,
        badge_service=container.resolve(services.badge.BadgeService)
    ).app)
    app.add_subapp('/slack', adapters.slack.SlackApplication(
        config=config,
        badge_service=container.resolve(services.badge.BadgeService)
    ).app)
    return app


def run_app():
    web.run_app(init_app([]), host=config['HTTP_HOST'], port=config['HTTP_PORT'])

if __name__ == '__main__':
    run_app()
