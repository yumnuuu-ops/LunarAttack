import pygame
from Weapon import Weapon

class Player:
    def __init__(self, assetMgr, x, y):
        self.image = assetMgr.getTexture("MainShip Full")
        self.rect = assetMgr.getRect("MainShip Full")
        self.health = 100
        self.pos = pygame.math.Vector2(x, y)
        self.speed = 10
        self.weapon = Weapon(assetMgr, x, y)

    #def shootBomb(self):

    def takeDamage(self, damage):
        self.health -= damage

    #def changeFireMode(self):

    def handle_mouse_input(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.pos.x = mouse_x - (self.rect.width / 2)
        self.pos.y = mouse_y - (self.rect.height / 2)

    def draw(self,surface):
        # draw weapon first
        self.weapon.draw(surface)

        # Sync physics position to the drawing rect
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        # Use its own stored self.image
        surface.blit(self.image, self.rect)

    def update(self):
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        self.handle_mouse_input()
        self.weapon.pos.x = self.rect.centerx - (self.weapon.rect.width / 2)
        self.weapon.pos.y = self.rect.centery - (self.weapon.rect.height / 2)
        self.weapon.rect.x = int(self.weapon.pos.x)
        self.weapon.rect.y = int(self.weapon.pos.y)

        mouse_buttons = pygame.mouse.get_pressed()
        is_firing = mouse_buttons[0]

        self.weapon.update(is_firing)

