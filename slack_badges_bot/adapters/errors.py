"""
Definición de excepciones personalizadas
"""

class BadgeCreateError(Exception):
    def __init__(self, description="None"):
        self.description = description
    def __repr__(self):
        return str(self.description)
