import logging
from slack_badges_bot.entities import Badge, BadgeImage
from io import BufferedIOBase
from pathlib import Path

class EntityService(object):
    def retrieve(self, id):
        return self.repository.load(id)

    def retrieve_ids(self):
        return self.repository.get_all_ids()

    def retrieve_all(self):
        entities = []
        for entity_id in self.retrieve_ids():
            entities.append(self.retrieve(entity_id))
        return entities



    def open_image(self, badge: Badge) -> BufferedIOBase:
        '''
        Sustituye el atributo image de Badge por un
        BadgeImage si no lo es y devuelve un descriptor
        del fichero de la imagen
        '''
        if isinstance(badge.image, str):
            if Path(badge.image).exists:
                badge.image = BadgeImage(path=badge.image, data=None)
            else:
                raise ValueError(f'BadgeService.open_image: path {badge.image} doesn\'t exist')
        if isinstance(badge.image, BadgeImage):
            return badge.image.get_data()
        raise TypeError(f'BadgeService.open_image: Can\'t open image of type {type(badge.image)}')
