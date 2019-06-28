"""Punto de entrada de la aplicación
"""
import punq

from aiohttp import web

from slack_badges_bot import adapters, services
from slack_badges_bot.adapters import api, slack

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


def init_app(argv):
    # TODO: Configurar logging para AIOHttp según la configuración
    app = web.Application()
    app.add_subapp('/api', api.WebService)
    app.add_subapp('slack', slack.SlackApplication)
    return app


def run_app():
    # Inyección de dependencias
    container = punq.Container()
    container.register(services.config.ConfigService)
    container.register(services.repositories.EntityRepository, adapters.repositories.EntityJsonRepository)

    config = container.resolve(services.config.ConfigReader)
    config = container.resolve(services.repositories.EntityRepository, path=config['DATA_PATH'])

    web.run_app(init_app([]), host=config['HTTP_HOST'], port=config['HTTP_PORT'])


if __name__ == '__main__':
    run_app()
