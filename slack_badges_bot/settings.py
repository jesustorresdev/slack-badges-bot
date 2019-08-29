"""Configuración por defecto de la aplicación.
"""
import os
import secrets

from pathlib import Path
from getpass import getpass


__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

class DefaultConfig:
    DEBUG = True

# API de openbadges
    API_URL = 'https://vituin-chat.iaas.ull.es/openbadges'
    API_BADGES = '/badges/{badge_id}/{requested_data}'
    API_AWARDS = '/awards/{award_id}/{requested_data}'
    API_ISSUER = '/issuer'
    BADGES_URL = API_URL + API_BADGES
    AWARDS_URL = API_URL + API_AWARDS
    ISSUER_URL = API_URL + API_ISSUER
    OPENBADGES_ISSUER_NAME = 'University of La Laguna SlackBot'
    OPENBADGES_ISSUER_DESCRIPTION = 'Herramienta para emitir medallas con las especificaciones de Open Badges'

# API de administración
    ADMIN_BADGES_CREATE = '/badges/create'
    ADMIN_PERMISSIONS_UPDATE = '/persons/permissions/update'
    ADMIN_PERMISSIONS_LIST = '/persons/permissions/list'
    ADMIN_PERSONS_LIST = '/persons/list'
    ADMIN_USER = 'admin'
    ADMIN_PASSWORD = secrets.ADMIN_PASSWORD

# Rutas de persistencia
    DATA_PATH = '../data'
    BADGES_PATH = '../data/badges'

# Opciones de configuración varias
    BADGE_NAME_MIN_LENGTH = 5
    BADGE_DESCRIPTION_MIN_LENGTH = 5
    BADGE_MIN_CRITERIA = 1

# Parámetros de slack
    SLACK_SIGNING_SECRET = secrets.SLACK_SIGNING_SECRET
    SLACK_OAUTH_ACCESS_TOKEN = secrets.SLACK_OAUTH_ACCESS_TOKEN
    SLACK_VERIFY_SECONDS = 5 * 60

# Sistema de permisos
    BADGES_ISSUE_SELF_P = 'awards:create:self'
    BADGES_ISSUE_OTHERS_P = 'awards:create:others'
    BADGES_LIST_P = 'badges:list'
    AWARDS_LIST_SELF_P = 'awards:list:self'
    AWARDS_LIST_OTHERS_P = 'awards:list:others'
    ALL_PERMISSIONS = [BADGES_ISSUE_SELF_P, BADGES_ISSUE_OTHERS_P, BADGES_LIST_P, AWARDS_LIST_SELF_P, AWARDS_LIST_OTHERS_P]
    USER_PERMISSIONS = [BADGES_LIST_P, AWARDS_LIST_SELF_P]

    # Ver https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app
    # Para los valores por defecto de estas opciones
    HTTP_HOST = None    # 0.0.0.0
    HTTP_PORT = 5000    # NGINX
