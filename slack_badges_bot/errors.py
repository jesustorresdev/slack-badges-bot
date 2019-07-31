"""
Definición de excepciones personalizadas
"""

class CustomError(Exception):
    def __init__(self, description="None"):
        self.description = description
    def __repr__(self):
        return str(self.description)


class BadgeCreateError(CustomError):
    pass

class BadgeImageError(CustomError):
    pass
