"""Colección de utilidades de propósito general.
"""
import importlib

__author__ = 'Jesús Torres'
__contact__ = "jmtorres@ull.es"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)


def import_string(import_name):
    """Importar un objeto en base a una cadena con una ruta de importación.

    :param import_name: La ruta al objeto a importar.
    :return: El objeto importado.
    """
    module_name, object_name = import_name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, object_name)
