import pygame
import utils


class Projectile(pygame.sprite.Sprite):
    def __init__(self, speed, x, y, vx, vy, damage):
        super().__init__()

        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 255, 0))

        self.rect = self.image.get_rect()
        self.rect.x = int(x)
        self.rect.y = int(y)

        self.pos = pygame.math.Vector2(x, y)
        self.vx = vx
        self.vy = vy
        self.speed = speed

        self.damage = damage

    def update(self):
        self.moveProjectile()

        #  Check if it went off screen, kill it if it did
        if utils.is_off_screen(self.pos.x, self.pos.y):
            self.kill()

    def moveProjectile(self):
        self.pos.x += self.vx * self.speed
        self.pos.y += self.vy * self.speed

        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)



