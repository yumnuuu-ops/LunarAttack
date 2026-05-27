import pygame
import random
import math
import utils
from Projectile import Projectile


class Alien(pygame.sprite.Sprite):
    def __init__(self, assetMgr, alien_type, x, y, stage=1, target_x=None, target_y=None):
        super().__init__()
        
        self.alien_type = alien_type
        
        # 1. Dynamically load the correct texture from AssetManager
        self.image = assetMgr.getTexture(alien_type)
        self.rect = self.image.get_rect()
        
        self.pos = pygame.math.Vector2(x, y)
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        
        # Target position coordinates for Stage 2 Formation entry
        self.target_x = target_x
        self.target_y = target_y
        
        if target_x is not None and target_y is not None:
            self.phase = "entering"
            self.shoot_cooldown = random.randint(60, 180) # Shoot every 1 to 3 seconds
        else:
            self.phase = "moving"
        
        # Configure base stats based on current Stage
        if stage == 1:
            self.hp = 10
            self.speed = 1.5
            self.movement_pattern = "pattern1"
        elif stage == 2:
            self.hp = 25
            self.speed = 2.0
            self.movement_pattern = "straight"
        else:  # Default/Fallback
            self.hp = 20
            self.speed = 3
            self.movement_pattern = "straight"
        
        self.max_hp = self.hp
        
        # variables for (zig-zag movement/sine wave pattern)
        # Spawning & swaying offsets
        self.spawn_x = x #original x position
        self.wave_time = 0
        self.wave_speed = 0.05
        self.wave_amplitude = 100

    def update(self):
        # Stage 2 Entry & Formation Logic
        if self.phase == "entering":
            # Move horizontally towards target_x
            if abs(self.pos.x - self.target_x) > self.speed:
                if self.pos.x < self.target_x:
                    self.pos.x += self.speed
                else:
                    self.pos.x -= self.speed
                
                # Apply the sinusoidal wave entry path!
                dist_x = abs(self.pos.x - self.target_x)
                total_dist = abs(self.spawn_x - self.target_x)
                if total_dist == 0:
                    total_dist = 1
                dampener = dist_x / total_dist
                
                # Wave up/down along a sine curve based on X position
                self.pos.y = self.target_y + math.sin(self.pos.x * 0.015) * 100 * dampener
            else:
                self.pos.x = self.target_x
                self.pos.y = self.target_y
                self.phase = "in_formation"

        elif self.phase == "in_formation":
            # Hover slightly up/down for a lively visual effect
            self.wave_time += 0.2
            self.pos.y = self.target_y + math.sin(self.wave_time) * 40

            # Shooting logic
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.shoot_cooldown = random.randint(60, 180) # Shoot every 1 to 3 seconds
                # Sync rect before shooting
                self.rect.x = int(self.pos.x)
                self.rect.y = int(self.pos.y)
                return self.shoot()

        else:
            # Standard Stage 1 / Moving Behavior
            if self.movement_pattern == "pattern1":
                self.pos.y += self.speed
                self.wave_time += self.wave_speed
                self.pos.x = self.spawn_x + (self.wave_amplitude * math.sin(self.wave_time))  
                
            elif self.movement_pattern == "pattern2":
                self.pos.y += self.speed
                self.wave_time += self.wave_speed
                self.pos.x = self.spawn_x + (self.wave_amplitude * math.sin(self.wave_time)) 
                
            else:  # "straight" movement
                self.pos.y += self.speed

        # Update the rect
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        
        # Cleanup if it goes off bottom of screen
        if self.pos.y > utils.SCREEN_H:
            self.kill()
        return None

    def shoot(self):
        bullet = Projectile(speed=5, x=self.rect.centerx, y=self.rect.bottom, vx=0, vy=1, damage=5)
        # Give enemy bullet a vibrant red color
        bullet.image.fill((255, 50, 50))
        return bullet

    def takeDamage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
