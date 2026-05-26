import pygame
from Projectile import Projectile

class Weapon:
    def __init__(self, assetMgr, x, y):
        self.image = assetMgr.getTexture("AutoCannon")
        self.rect = assetMgr.getRect("AutoCannon")
        self.pos = pygame.math.Vector2(x, y)
        self.fireRate = 1
        self.projectileCount = 1
        self.projectileSize = 1
        self.projectileType = "cannon"
        self.projectileSpeed = 20

        self.damage = 10

    def shootLaser(self):
        projStartingPosX = self.rect.centerx
        projStartingPosY = self.rect.top

        # Up velocity
        vx = 0
        vy = -1
                         # (speed, x, y, vx, vy, damage):
        new_projectile = Projectile(self.projectileSpeed, projStartingPosX, projStartingPosY, vx, vy, self.damage)

        return new_projectile

    def draw(self, surface):
        # Use its own stored self.image
        surface.blit(self.image, self.rect)