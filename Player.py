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

    def handle_keyboard_input(self):
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0

        if keys[pygame.K_a]:  # Move Left
            move_x -= 1
        if keys[pygame.K_d]:  # Move Right
            move_x += 1
        if keys[pygame.K_w]:  # Move Up
            move_y -= 1
        if keys[pygame.K_s]:  # Move Down
            move_y += 1

        # Update the physics position based on direction and speed
        self.pos.x += move_x * self.speed
        self.pos.y += move_y * self.speed

        # Snap the visible rectangle hitbox to the floating point position
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        # horizontal screen clamp
        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x > 1280 - self.rect.width:
            self.pos.x = 1280 - self.rect.width

        # horizontal vertical clamp
        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y > 720 - self.rect.height:
            self.pos.y = 720 - self.rect.height


    def draw(self,surface):
        # draw weapon first
        self.weapon.draw(surface)

        # Sync physics position to the drawing rect
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        # Use its own stored self.image
        surface.blit(self.image, self.rect)

    def update(self):
        self.handle_keyboard_input()

        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        self.weapon.pos.x = self.rect.centerx - (self.weapon.rect.width / 2)
        self.weapon.pos.y = self.rect.centery - (self.weapon.rect.height / 2)
        self.weapon.rect.x = int(self.weapon.pos.x)
        self.weapon.rect.y = int(self.weapon.pos.y)

        mouse_buttons = pygame.mouse.get_pressed()
        is_firing = mouse_buttons[0]

        self.weapon.update(is_firing)

    def apply_push(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy

