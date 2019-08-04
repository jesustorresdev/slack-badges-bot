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
        if self.path:
            assert isinstance(self.path, str), f'path of type {type(self.path)} not allowed'
            self.path = Path(self.path)
            self.suffix = self.path.suffix[1:] # quitar el "." de ".png"
        if self.data:
            assert isinstance(self.data, BufferedIOBase), f'data of type {type(self.data)} not allowed'
            self.data = self.data
            self.data.seek(0)
            self.suffix = str(PILImage.open(self.data).format).lower()

    def get_data(self):
        ''' Método para acceder a self.data
        Carga la imagen si no está en memoria
        '''
        if self.data is None:
            assert self.path is not None
            self.data = open(self.path, 'rb')
        self.data.seek(0)
        return self.data
