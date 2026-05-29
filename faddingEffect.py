import pygame
from globals import particle_group

class FadingGhost(pygame.sprite.Sprite):
    def __init__(self, image, center_x, center_y):
        super().__init__()
        # Store original image for scaling
        self.original_image = image.copy()
        self.image = image.copy()
        
        # Position
        self.pos = pygame.math.Vector2(center_x, center_y)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        # Fading & Drifting physical properties (Option 3: Drifting Celestial Vapor)
        self.alpha = 255
        self.scale = 1.0
        self.fade_speed = 8         # Speed of transparency fadeout
        self.shrink_rate = 0.97      # Smooth scaling down per frame
        self.drift_vy = -0.8        # Slow upward drift speed (zero gravity)

    def update(self):
        # 1. Update properties
        self.alpha -= self.fade_speed
        self.pos.y += self.drift_vy
        self.scale *= self.shrink_rate
        
        # 2. Check if finished/dead
        if self.alpha <= 0 or self.scale <= 0:
            self.kill()
            return
            
        # 3. Calculate scaled dimensions
        w, h = self.original_image.get_size()
        new_w = int(w * self.scale)
        new_h = int(h * self.scale)
        if new_w <= 0 or new_h <= 0:
            self.kill()
            return
            
        # 4. Re-draw the scaled and faded ghost sprite
        scaled_img = pygame.transform.scale(self.original_image, (new_w, new_h))
        scaled_img.set_alpha(self.alpha)
        
        self.image = scaled_img
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

class faddingEffect:
    @staticmethod
    def trigger(entity):
        # Spawns a single beautiful drifting celestial ghost fade particle
        ghost = FadingGhost(entity.image, entity.rect.centerx, entity.rect.centery)
        particle_group.add(ghost)
