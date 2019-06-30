"""Servicio de configuración de la aplicación.
"""
from pathlib import Path

from slack_badges_bot.utils import import_string

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


class ConfigService(dict):
    """Servicio de configuración

    :param defaults: Diccionario de valores por defecto
    """

    def __init__(self, defaults=None):
        super().__init__(defaults or {})

    def from_object(self, obj):
        """Actualizar los valores de configuración a partir de los atributos del objeto indicado.

        El objeto puede ser uno de los siguientes dos tipos:

         * Una cadena: En cuyo caso el objeto con ese nombre será importado.
         * Una instancia: En cuyo caso será usada directamente.

        Solo se cargarán atributos en mayúsculas.

        :param obj: Un nombre a importar o un objeto
        """
        if isinstance(obj, str):
            obj = import_string(obj)
        self.update({key: getattr(obj, key) for key in dir(obj) if key.isupper()})

    def option_as_path(self, option, default=None):
        """Recuperar una opción de configuración interpretándola como una ruta en el sistema de archivos

        :param option: Nombre de la opción a recuperar.
        :param default: Valor a devolver si la opción no existe.

        :return: Objecto pathlib.Path con la ruta indicada si la opción existe o el valor de  default si no existe.
        """
        path = self.get(option)
        return default if path is None else Path(path)
