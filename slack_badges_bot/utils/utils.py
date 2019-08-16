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


def info(object, spacing=10, collapse=1):
    """Print methods and doc strings.
    Takes module, class, list, dictionary, or string."""
    methodList = [method for method in dir(object) if callable(getattr(object, method))]
    processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
    print ("\n".join(["%s %s" %
                    (method.ljust(spacing),
                    processFunc(str(getattr(object, method).__doc__)))
                    for method in methodList]))
