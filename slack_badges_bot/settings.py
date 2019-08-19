"""Configuración por defecto de la aplicación.
"""
import os

from pathlib import Path


__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

class DefaultConfig:
    DEBUG = True
    API_URL = 'http://vituin-chat.iaas.ull.es/openbadges'
    BADGES_URL = f'{API_URL}/badges'
    AWARDS_URL = f'{API_URL}/awards'
    BADGES_JSON_URL = f'{BADGES_URL}' + '/{}/json' # se usa .format para insertar el id
    BADGES_IMAGE_URL = f'{BADGES_URL}' + '/{}/image' # se usa .format para insertar el id
    BADGES_CRITERIA_URL = f'{BADGES_URL}' + '/{}/criteria' # se usa .format para insertar el id
    AWARDS_JSON_URL = f'{AWARDS_URL}' + '/{}/json' # se usa .format para insertar el id
    AWARDS_IMAGE_URL = f'{AWARDS_URL}' + '/{}/image' # se usa .format para insertar el id
    ISSUER_URL = f'{API_URL}/issuer'
    ISSUER_ID = 'issuer' # nombre del json en data/issuer/
    REVOCATION_URL = f'{API_URL}/revocation'
    DATA_PATH = '../data'
    BADGES_PATH = '../data/badges'
    BADGE_NAME_MIN_LENGTH = 5
    BADGE_DESCRIPTION_MIN_LENGTH = 5
    BADGE_MIN_CRITERIA = 1
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_OAUTH_ACCESS_TOKEN = os.getenv('SLACK_OAUTH_ACCESS_TOKEN')
    SLACK_VERIFY_SECONDS = 5 * 60

    # Ver https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app
    # Para los valores por defecto de estas opciones
    HTTP_HOST = None    # 0.0.0.0
    HTTP_PORT = 5000    # NGINX
