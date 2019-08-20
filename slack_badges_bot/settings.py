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

# API de openbadges
    API_URL = 'http://vituin-chat.iaas.ull.es/openbadges'
    API_BADGES = '/badges/{badge_id}/{requested_data}'
    API_AWARDS = '/awards/{award_id}/{requested_data}'
    API_ISSUER = '/issuer'
    BADGES_URL = API_URL + API_BADGES
    AWARDS_URL = API_URL + API_AWARDS
    ISSUER_URL = API_URL + API_ISSUER
    OPENBADGES_ISSUER_NAME = 'Slack Badges Bot'
    OPENBADGES_ISSUER_DESCRIPTION = 'Herramienta para emitir medallas que une el chat de Slack con el estándar de OpenBadges'

# API de administración
    CREATE_BADGE_PATH = '/badges/create'

# Rutas de persistencia
    DATA_PATH = '../data'
    BADGES_PATH = '../data/badges'

# Opciones de configuración varias
    BADGE_NAME_MIN_LENGTH = 5
    BADGE_DESCRIPTION_MIN_LENGTH = 5
    BADGE_MIN_CRITERIA = 1
# Parámetros de slack
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_OAUTH_ACCESS_TOKEN = os.getenv('SLACK_OAUTH_ACCESS_TOKEN')
    SLACK_VERIFY_SECONDS = 5 * 60

    # Ver https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app
    # Para los valores por defecto de estas opciones
    HTTP_HOST = None    # 0.0.0.0
    HTTP_PORT = 5000    # NGINX
