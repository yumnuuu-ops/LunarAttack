import pygame
import utils
import random

class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, assetMgr, speed, x, y, vx, vy, damage):
        super().__init__()
        self.assetMgr = assetMgr
        
        # Get loaded texture from asset manager
        self.original_image = assetMgr.getTexture("enemy_bullet")
        if self.original_image is None:
            # Fallback if texture not loaded
            self.original_image = pygame.Surface((8, 16))
            self.original_image.fill((255, 50, 50))
            
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.damage = damage
        
        # Spin values for rich dynamics
        self.angle = random.randint(0, 360)
        self.rot_speed = random.choice([-8, -6, 6, 8]) # Random direction and speed

    def update(self):
        # Move projectile
        self.pos.x += self.vx * self.speed
        self.pos.y += self.vy * self.speed
        
        # Rotate image
        self.angle = (self.angle + self.rot_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Update rect keeping the center stable!
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        if utils.is_off_screen(self.pos.x, self.pos.y):
            self.kill()

