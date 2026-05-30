import pygame
from Weapon import Weapon
from globals import assetMgr, soundMgr
import globals as g
from ShatterEffect import ShatterEffect

class Player:
    def __init__(self, x, y):
        self.image = assetMgr.getTexture("MainShip Full")
        self.rect = assetMgr.getRect("MainShip Full")
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 4
        self.pos = pygame.math.Vector2(x, y)
        self.speed = 10

        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        self.weapon = Weapon(x, y)

        self.invincible = False
        self.invincibility_timer = 0.0
        self.blink_timer = 0.0
        self.visible = True

    #def shootBomb(self):

    def takeDamage(self, damage):
        if self.invincible:
            return
        self.hp -= damage
        if hasattr(self, 'trigger_shake') and self.trigger_shake:
            self.trigger_shake(10, 15)

        if self.hp > 0 :
            soundMgr.play_sfx("player hit")
        elif self.hp == 0:
            soundMgr.play_sfx("player dies")

        self.invincible = True
        self.invincibility_timer = 2.0  # invincibility of 2 seconds
        self.blink_timer = 0.0
        self.visible = False

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

        # Snap the visible rectangle hitbox to the floating point position
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)


    def draw(self,surface):
        if self.visible:

            # draw weapon first
            self.weapon.draw(surface)

            # Sync physics position to the drawing rect
            self.rect.x = int(self.pos.x)
            self.rect.y = int(self.pos.y)

            surface.blit(self.image, self.rect)
        # PLAYER HIT BOX
        if hasattr(self, 'mask') and self.mask:
            for point in self.mask.outline():
                pixel_x = self.rect.x + point[0]
                pixel_y = self.rect.y + point[1]
                surface.set_at((pixel_x, pixel_y), (0, 255, 0))


    def update(self, events):
        self.handle_keyboard_input()

        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        self.weapon.pos.x = self.rect.centerx - (self.weapon.rect.width / 2)
        self.weapon.pos.y = self.rect.centery - (self.weapon.rect.height / 2)
        self.weapon.rect.x = int(self.weapon.pos.x)
        self.weapon.rect.y = int(self.weapon.pos.y)

        mouse_buttons = pygame.mouse.get_pressed()
        is_firing = mouse_buttons[0]

        self.weapon.update(is_firing, events)

        if self.invincible:
            self.invincibility_timer -= g.dt
            self.blink_timer += g.dt

            # Toggle player visibility every 0.1 seconds
            if self.blink_timer >= 0.1:
                self.visible = not self.visible
                self.blink_timer = 0.0

            # When 2 seconds are up, return the ship to normal
            if self.invincibility_timer <= 0:
                self.invincible = False
                self.visible = True

    def apply_push(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy
