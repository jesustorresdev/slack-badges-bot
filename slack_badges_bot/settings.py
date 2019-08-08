"""Configuración por defecto de la aplicación.
"""
from pathlib import Path

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class DefaultConfig:
    DEBUG = True
    API_URL = 'http://vituin-chat.iaas.ull.es/api'
    BADGES_URL = f'{API_URL}/badges'
    DATA_PATH = '../data'  # Relativo al directorio de trabajo de la aplicación
    BADGES_PATH = '../data/badges'
    BADGE_NAME_MIN_LENGTH = 5
    BADGE_DESCRIPTION_MIN_LENGTH = 5
    BADGE_MIN_CRITERIA = 1

    # Ver https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app
    # Para los valores por defecto de estas opciones
    HTTP_HOST = None    # 0.0.0.0
    HTTP_PORT = 5000    # NGINX
