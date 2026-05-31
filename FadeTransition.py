import pygame

class FadeTransition:
    def __init__(self, screen_w, screen_h, fade_speed=255):
        self.fade_surface = pygame.Surface((screen_w, screen_h))
        self.fade_surface.fill((0, 0, 0))
        self.fade_speed = fade_speed

        # Start at 255 (black) for a fade-in, or 0 (clear) for a fade-out
        self.fade_alpha = 255
        self.fading_in = True

    def update(self, dt):
        if self.fading_in:
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading_in = False
        else:
            # Increase alpha over time (e.g., 255 alpha / 2 seconds = 127.5 speed)
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255

    def draw(self, surface):
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            surface.blit(self.fade_surface, (0, 0))