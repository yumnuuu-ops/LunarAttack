import pygame
import random

class DummyEnemy:
    def __init__(self, screen_w, screen_h):
        self.sw     = screen_w
        self.sh     = screen_h
        self.size   = 40
        self.points = 100
        self.spawn()

    def spawn(self):
        self.x = random.randint(100, self.sw - 100)
        self.y = random.randint(60, self.sh // 2)
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.alive = True

    def check_hit(self, projectile_group):
        for proj in projectile_group:
            if self.rect.colliderect(proj.rect):
                proj.kill()
                self.alive = False
                return True
        return False

    def draw(self, screen):
        if self.alive:
            pygame.draw.rect(screen, (200, 50, 50), self.rect, border_radius=4)
            pygame.draw.rect(screen, (255, 100, 100), self.rect, 2, border_radius=4)