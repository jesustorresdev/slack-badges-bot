from io import BytesIO
from pathlib import Path, PosixPath
from typing import Union
from errors import *
from PIL import Image
import inspect

__author__ = 'Martín Belda'
__contact__ = "mbelda@gmail.com"
__license__ = "Apache License, Version 2.0"
__copyright__ = "Copyright 2019 {0} <{1}>".format(__author__, __contact__)

class BadgeImage:
    """
    Clase para gestionar las imágenes en memoria.
    """
    def __init__(self, image: Union[BytesIO, str]):
        print(f'Creando un BadgeImage image:{type(image)}')
        print(f'Llamado desde {inspect.stack()[1].filename}')
        print(f'Llamado desde {inspect.stack()[1].lineno}')
        print(f'Llamado desde {inspect.stack()[1].function}')
        print(f'Llamado desde {inspect.stack()[1].code_context}')
        if isinstance(image, BytesIO):
            self.loaded = True
        elif isinstance(image, (str, Path, PosixPath)):
            print(f'BadgeImage({image})')
            image = Path(image)
            if not image.exists():
                raise BadgeCreateError(f'file {image} doesn\'t exist')
            self.loaded = False
        else:
            raise TypeError(f'{self.__class__.__name__}: {image} of type {type(image)} not allowed')
        self.image = image

    def _load_image(self):
        if not self.loaded:
            assert isinstance(self.image, Path)
            with self.image.open('rb') as f:
                self.image = BytesIO(f.read())
            self.loaded = True
        assert isinstance(self.image, BytesIO)
        return self.image

    def get(self):
        return self._load_image()

    def get_type(self):
        self._load_image()
        self.image.seek(0)
        return str(Image.open(self.image).format).lower()
