import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z):
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.name = 'Tile'

class CollideTile(Tile):
    def __init__(self, pos, surf, groups, z):
        super().__init__(pos, surf, groups, z)

        self.oldrect = self.rect.copy()


        