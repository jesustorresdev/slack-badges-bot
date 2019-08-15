import logging

from dataclasses import dataclass
from pathlib import Path
from io import BufferedIOBase
from PIL import Image as PILImage

__author__ = 'Martín Belda'
__contact__ = "mbelda@gmail.com"
__license__ = "apache license, version 2.0"
__copyright__ = "copyright 2019 {0} <{1}>".format(__author__, __contact__)

'''
Clase que puede guardar una imagen de dos maneras
1. Guardando la ruta de la imagen en Image.path
2. Guardando los datos de la imagen en Image.data
Para acceder a data se usa la función get_data
'''
@dataclass
class BadgeImage:
    path: Path
    data: BufferedIOBase
    suffix: str = None

    def __post_init__(self):
        if self.data: # Cuando se crea con imagen bytes
            assert isinstance(self.data, BufferedIOBase), f'data of type {type(self.data)} not allowed'
            self.data = self.data
            self.data.seek(0)
            self.suffix = str(PILImage.open(self.data).format).lower()
        else: # Cuando se carga desde el repositorio
            assert self.path is not None, f'None path and None data not allowed!'
            assert isinstance(self.path, str), f'path of type {type(self.path)} not allowed'
            self.path = Path(self.path)
            self.suffix = self.path.suffix[1:] # quitar el "." de ".png"

    def get_data(self):
        ''' Método para acceder a self.data
        Abre el fichero y devuelve el descriptor de fichero de la imagen.
        En llamadas posteriores sólo devuelve el descriptor de fichero ya abierto.
        '''
        if self.data is None:
            self.data = open(self.path, 'rb')
        self.data.seek(0)
        return self.data
