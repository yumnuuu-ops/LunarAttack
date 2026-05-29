import random
import pygame

class ShatterParticle(pygame.sprite.Sprite):
    def __init__(self, chunk_surface, x, y):
        super().__init__()
        tight_box = chunk_surface.get_bounding_rect()
        trimmed_surface = chunk_surface.subsurface(tight_box)
        self.image = trimmed_surface.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Random directions
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.alpha = 255

    def update(self):
        # Move
        self.rect.x += self.vx
        self.rect.y += self.vy

        self.alpha -= 8
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)