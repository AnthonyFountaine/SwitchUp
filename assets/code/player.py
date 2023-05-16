import pygame
from assets.code.settings import *
from pygame import Vector2
from os import walk

class Player(pygame.sprite.Sprite):
    def __init__(self, group, path, collide, spikes, play, pos, end, clear, gshift):
        super().__init__(group)
        self.allsprites = group

        self.start = pos

        self.name = 'Player'

        self.animationpath = path

        self.import_assets(self.animationpath)

        self.playerstatus = 'right_idle'
        self.oldplayerstatus = self.playerstatus
        self.frameindex = 0

        self.image = self.animations[self.playerstatus][self.frameindex]
        self.rect = self.image.get_rect(center = (pos[0] - self.image.get_width()//2, pos[1] - self.image.get_height()//2))
        self.rect.width -= 12
        self.rect.height -= 7
        self.oldrect = self.rect.copy()
        self.z = Layers['collides']


        self.jumpspeed = 225
        self.gravityconst = 10
        self.floorstatus = False
        
        self.position = Vector2(self.rect.center)
        self.direction = Vector2()
        self.speed = 250

        self.collidegroup = collide
        self.spikegroup = spikes
        self.gshift = gshift
        self.newmap = play

        self.lvlend = end
        self.cleargroups = clear
        self.gdelay = 0

    def import_assets(self,path):
        self.animations = {}

        for index, folder_name in enumerate(walk(path)):
            if index == 0:
                for folder in folder_name[1]:
                    self.animations[folder] = []
            

            else:
                for index, file_name in enumerate(folder_name[2]):
                    newpath = folder_name[0].replace('\\', '/')
                    slash = newpath.rfind('/')
                    folder = newpath[slash+1:]
                    image = pygame.transform.scale(
                        pygame.image.load(newpath + '/' + file_name).convert_alpha(),
                        (32,32)
                    )
                    self.animations[folder].append(image)
    
    def animate(self, dt):
        self.frameindex += 25 * dt
        if self.frameindex >= len(self.animations[self.playerstatus]):
            self.frameindex = 0
        self.image = self.animations[self.playerstatus][min(int(self.frameindex), 17)]

    def move(self,dt):
        self.position.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.position.x)

        self.direction.y += self.gravityconst
        self.position.y += self.direction.y * dt
        self.rect.y = round(self.position.y)


        self.horicollide()
        self.vertcollide()


    def horicollide(self):
        for sprite in self.collidegroup.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.rect.left <= sprite.rect.right and self.oldrect.left >= sprite.oldrect.right:
                    self.rect.left = sprite.rect.right
                if self.rect.right >= sprite.rect.left and self.oldrect.right <= sprite.oldrect.left:
                    self.rect.right = sprite.rect.left
                self.position.x = self.rect.x
        if self.rect.left<0:
            self.rect.left = 0
        if self.rect.right>1280:
            self.rect.right = 1280

        for sprite in self.lvlend.sprites():
            if self.rect.colliderect(sprite.rect):
                if self.keys[pygame.K_e]:
                    for sprite in self.allsprites.sprites():
                        if hasattr(sprite, 'name'):
                            if sprite.name == 'Player':
                                pass
                            else:
                                sprite.kill()
                        else:
                            sprite.kill()
                    for group in self.cleargroups:
                        group.empty()
                    self.newmap()

        for sprite in self.gshift:
            if self.rect.colliderect(sprite.rect) and self.gdelay<0:
                self.gravityconst = -self.gravityconst
                self.jumpspeed = -self.jumpspeed
                self.gdelay = 30
    
    def vertcollide(self):
        for sprite in self.collidegroup.sprites():
            if sprite.rect.colliderect(self.rect):
                if self.rect.bottom >= sprite.rect.top and self.oldrect.bottom <= sprite.oldrect.top:
                    self.rect.bottom = sprite.rect.top
                    if self.gravityconst >0:
                        self.floorstatus = True
                if self.rect.top <= sprite.rect.bottom and self.oldrect.top >= sprite.oldrect.bottom:
                    self.rect.top = sprite.rect.bottom
                    if self.gravityconst <0:
                        self.floorstatus = True
                self.position.y = self.rect.y
                self.direction.y = 0

        if self.floorstatus and self.direction.y != 0:
            self.floorstatus = False
        
    def spikecollide(self):
        for sprite in self.spikegroup.sprites():
            if sprite.rect.colliderect(self.rect) or self.rect.bottom<0 or self.rect.top>960:
                 self.rect.center = self.start[0] - self.image.get_width()//2, self.start[1] - self.image.get_height()//2
                 self.position = pygame.math.Vector2(self.rect.center)
                 self.gravityconst = 10
                 self.jumpspeed = 225
                

    def update_status(self):
        if self.direction.x == 0 and self.floorstatus:
            self.playerstatus = self.playerstatus.split('_')[0] + '_idle'
        if self.direction.y <= 0 and not self.floorstatus:
            self.playerstatus = self.playerstatus.split('_')[0] + '_jump'

    def fix_floor(self):
        floor_rect = pygame.Rect(0,0,self.rect.width,5)
        if self.gravityconst >0:
            floor_rect.midtop = self.rect.midbottom
        if self.gravityconst <0:
            floor_rect.midbottom = self.rect.midtop

        for sprite in self.collidegroup:
            if sprite.rect.colliderect(floor_rect):
                if self.gravityconst >0:
                    if self.direction.y > 0:
                        self.floorstatus = True
                if self.gravityconst <0:
                    if self.direction.y <0:
                        self.floorstatus = True
                

    def input(self):
        self.keys = pygame.key.get_pressed()
                    
        if self.keys[pygame.K_a]:
            self.direction.x = -1
            self.playerstatus = 'left'
        elif self.keys[pygame.K_d]:
            self.direction.x = 1
            self.playerstatus = 'right'
        else:
            self.direction.x = 0

        if self.keys[pygame.K_SPACE] and self.floorstatus == True:
            self.direction.y = -self.jumpspeed

    def update(self,dt):
        self.animate(dt)
        self.update_status()
        self.input()
        self.move(dt)
        self.fix_floor()
        self.spikecollide()
        self.oldrect = self.rect.copy()
        self.gdelay-=1