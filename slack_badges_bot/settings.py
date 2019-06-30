"""Configuración por defecto de la aplicación.
"""
from pathlib import Path

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class DefaultConfig:
    DEBUG = True
    DATA_PATH = 'data'  # Relativo al directorio de trabajo de la aplicación

    # Ver https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.run_app
    # Para los valores por defecto de estas opciones
    HTTP_HOST = None    # 0.0.0.0
    HTTP_PORT = None    # 8080 para HTTP y 8443 para HTTPS
