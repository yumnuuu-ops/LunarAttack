import pygame
import utils
from globals import assetMgr
import random

class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, speed, x, y, vx, vy, damage):
        super().__init__()
        # Get loaded texture from asset manager
        self.original_image = assetMgr.getTexture("enemy_bullet")

        w, h = self.original_image.get_size()
        self.image = pygame.transform.scale_by(self.original_image, 0.8)
        self.rect = self.image.get_rect()
        
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.damage = damage

    def update(self):
        # Move projectile
        self.pos.x += self.vx * self.speed
        self.pos.y += self.vy * self.speed
        
        # Update rect keeping the center stable!
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        if utils.is_off_screen(self.pos.x, self.pos.y):
            self.kill()

