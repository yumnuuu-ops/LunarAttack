import pygame
import random
import math
import utils
from AnimationManager import AnimationManager
from SparksEffect import SparksEffect
from ShatterEffect import ShatterEffect
from globals import assetMgr, soundMgr
from enemy.EnemyProjectile import EnemyProjectile

class Alien(pygame.sprite.Sprite):
    def __init__(self, alien_type, x, y, stage=1, target_x=None, target_y=None):
        super().__init__()
        self.alien_type = alien_type
        animation = assetMgr.getAnim(alien_type)
        self.animator = AnimationManager(animation, 14)
        raw_image = self.animator.get_current_frame()
        tight_box = raw_image.get_bounding_rect()
        self.image = raw_image.subsurface(tight_box)

        self.rect = self.image.get_rect()
        if stage == 1:
            y = -100
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # Target position coordinates for Stage 2 Formation entry
        self.target_x = target_x
        self.target_y = target_y
        self.time_alive = 0.0
        self.stage = stage
        
        if target_x is not None and target_y is not None:
            self.phase = "entering"
            if stage == 4:
                self.shoot_cooldown = random.randint(240, 480)
            elif stage == 5:
                self.shoot_cooldown = random.randint(180, 360)
            else:
                self.shoot_cooldown = random.randint(60, 180) # Shoot every 1 to 3 seconds
        else:
            if stage == 4:
                self.shoot_cooldown = random.randint(240, 480)
            elif stage == 5:
                self.shoot_cooldown = random.randint(180, 360)
            else:
                self.shoot_cooldown = random.randint(60, 180)
            if stage in [2, 3]:
                self.phase = "stage2_align"
                self.target_y = y
                self.align_timer = random.randint(60, 100)
                self.dive_vx = 0
                self.dive_vy = 0
            else:
                self.phase = "moving"
        
        # Configure base stats based on current Stage
        if stage == 1:
            self.hp = 50
            self.speed = 2
            self.movement_pattern = "pattern1"
        elif stage == 2:
            self.hp = 60
            self.speed = 3
            self.movement_pattern = "sine"
        elif stage == 3:
            self.hp = 60
            self.speed = 4
            self.movement_pattern = "sine"
        elif stage == 4:
            self.hp = 55
            self.speed = 3
            self.movement_pattern = "straight"
        elif stage == 5:
            self.hp = 55
            self.speed = 4
            self.movement_pattern = "straight"
        
        self.max_hp = self.hp

        # Dynamically scale shield HP based on original/max HP
        if self.alien_type == "tendril_alien":
            self.shield_hp = max(1, int(self.hp * 1.00))  # Increased shield strength to 100% of max HP
        else:
            self.shield_hp = 0
        
        # variables for (zig-zag movement/sine wave pattern)
        # Spawning & swaying offsets
        self.spawn_x = x #original x position
        self.wave_time = 10
        self.wave_speed = 0.05
        self.wave_amplitude = 100

        # Special stage 4/5 effect state variables
        self.enemy_alpha = 255
        self.enemy_scale = 1.0
        self.particles = []
        self.spawned_particles = False

    def update(self, player_pos=None, player_touching_edge=False):
        # update animation
        self.animator.update()
        self.image = self.animator.get_current_frame()

        fired_bullet = None

        if self.phase == "spawning_portal":
            self.portal_age += 1
            progress = min(1.0, self.portal_age / 45)
            self.enemy_alpha = min(255, self.portal_age * 7)
            self.enemy_scale = 0.65 + progress * 0.35
            
            if self.portal_age >= 45:
                self.phase = "entering"
                self.enemy_alpha = 255
                self.enemy_scale = 1.0
                self.spawn_x = self.pos.x

        # Stage 2 Entry & Formation Logic
        if self.phase == "spawning_portal":
            pass  # Keep completely stationary during portal emergence!
        elif self.phase == "stationary":
            # Hover slightly up/down for a lively visual effect
            self.wave_time += 0.2
            self.pos.y = self.target_y + math.sin(self.wave_time) * 1

            # Keep cooldown ticking to drive the laser sight blinking cycle, but do NOT fire any bullets!
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                self.shoot_cooldown = random.randint(60, 150)

        elif self.phase == "entering":
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
            self.pos.y = self.target_y + math.sin(self.wave_time) * 1

            # Shooting logic
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                if self.stage == 4:
                    self.shoot_cooldown = random.randint(240, 480) # Stage 4: Shoot every 4 to 8 seconds
                elif self.stage == 5:
                    self.shoot_cooldown = random.randint(180, 360) # Stage 5: Shoot every 3 to 6 seconds
                else:
                    self.shoot_cooldown = random.randint(60, 180) # Default: Shoot every 1 to 3 seconds
                # Sync rect before shooting
                self.rect.x = int(self.pos.x)
                self.rect.y = int(self.pos.y)
                fired_bullet = self.shoot(player_pos)

        elif self.phase == "stage2_align":
            # Keep plane off-screen and stationary horizontally at its spawn position
            self.pos.y = self.target_y

            self.align_timer -= 1
            if self.align_timer <= 0:
                # Lock in direction targeting the player
                if player_pos is not None:
                    dx = player_pos[0] - self.pos.x
                    dy = player_pos[1] - self.pos.y
                else:
                    dx = 0
                    dy = 500
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.dive_vx = dx / dist
                    self.dive_vy = dy / dist
                else:
                    self.dive_vx = 0
                    self.dive_vy = 1
                self.phase = "stage2_dive"

        elif self.phase == "stage2_dive":
            current_speed = self.speed
            if player_touching_edge:
                current_speed = self.speed * 2.5
            
            # Crash at you (dive-bomb)! Move along the locked vector at 2.8x speed
            self.pos.x += self.dive_vx * current_speed * 2.8
            self.pos.y += self.dive_vy * current_speed * 2.8

        else:
            current_speed = self.speed
            if self.stage in [2, 3] and player_touching_edge:
                current_speed = self.speed * 2.5

            # Standard Stage 1 / Moving Behavior
            if self.movement_pattern == "pattern1":
                self.pos.y += current_speed
                self.wave_time += self.wave_speed
                self.pos.x = self.spawn_x + (self.wave_amplitude * math.sin(self.wave_time))  
                
            elif self.movement_pattern == "pattern2":
                self.pos.y += current_speed
                self.wave_time += self.wave_speed
                self.pos.x = self.spawn_x + (self.wave_amplitude * math.sin(self.wave_time)) 
                
            elif self.movement_pattern == "sine":
                self.pos.y += current_speed
                self.wave_time += self.wave_speed
                self.pos.x = self.spawn_x + (self.wave_amplitude * math.sin(self.wave_time * 1.5))
                
            else:  # "straight" movement
                self.pos.y += current_speed

        # Update the rect and dynamic thruster fire tail
        raw_image = self.animator.get_current_frame()
        
        if self.phase == "stage2_align":
            # Completely invisible off-screen targeting phase!
            self.image = pygame.Surface((0, 0), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        else:
            # Crop to the actual boundaries of the plane first
            tight_box = raw_image.get_bounding_rect()
            base_image = raw_image.subsurface(tight_box)
            
            if getattr(self, 'shield_hp', 0) > 0:
                self.time_alive += 1/60.0
                pulse = (math.sin(self.time_alive * 8) + 1) / 2
                alpha = int(100 + 155 * pulse)
                color = (255, 50, 150) # Neon Pink/Purple
                
                mask = pygame.mask.from_surface(base_image)
                sil = mask.to_surface(setcolor=(*color, alpha), unsetcolor=(0, 0, 0, 0))
                
                thickness = 4 + int(pulse * 3)
                w, h = base_image.get_size()
                
                shielded_image = pygame.Surface((w + thickness*2, h + thickness*2), pygame.SRCALPHA)
                
                shielded_image.blit(sil, (0, thickness))
                shielded_image.blit(sil, (thickness*2, thickness))
                shielded_image.blit(sil, (thickness, 0))
                shielded_image.blit(sil, (thickness, thickness*2))
                
                shielded_image.blit(sil, (0, 0))
                shielded_image.blit(sil, (thickness*2, thickness*2))
                shielded_image.blit(sil, (0, thickness*2))
                shielded_image.blit(sil, (thickness*2, 0))
                
                shielded_image.blit(base_image, (thickness, thickness))
                self.image = shielded_image
            else:
                self.image = base_image
            
            if self.phase == "stage2_dive":
                # Rotate the plane and the flame to face the movement/dive vector perfectly
                deg = math.degrees(math.atan2(self.dive_vy, self.dive_vx))
                rotation_angle = 90.0 - deg
                rotated_img = pygame.transform.rotate(self.image, rotation_angle)
                # Crop transparent padding to keep the hit-box as tight as possible
                tight_rotated_box = rotated_img.get_bounding_rect()
                self.image = rotated_img.subsurface(tight_rotated_box)
                
            # Scale and set alpha for portal/dissolve effects
            enemy_scale = getattr(self, "enemy_scale", 1.0)
            enemy_alpha = getattr(self, "enemy_alpha", 255)
            
            if enemy_scale != 1.0 or enemy_alpha != 255:
                w, h = self.image.get_size()
                new_w = max(1, int(w * enemy_scale))
                new_h = max(1, int(h * enemy_scale))
                self.image = pygame.transform.smoothscale(self.image, (new_w, new_h))
                self.image.set_alpha(max(0, min(255, int(enemy_alpha))))
                
            self.rect = self.image.get_rect()
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # Cleanup if it goes off bottom of screen
        if self.pos.y > utils.SCREEN_H:
            self.kill()
        return fired_bullet

    def shoot(self, player_pos=None):
        vx = 0
        vy = 1
        if self.stage in [4, 5] and player_pos is not None:
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.bottom
            dist = math.hypot(dx, dy)
            if dist > 0:
                vx = dx / dist
                vy = dy / dist
        bullet = EnemyProjectile(5, self.rect.centerx, self.rect.bottom, vx, vy, 5)
        return bullet

    def takeDamage(self, damage):
        if getattr(self, 'shield_hp', 0) > 0:
            self.shield_hp -= damage
            if self.shield_hp <= 0:
                soundMgr.play_sfx("shield break")
            return
            
        self.hp -= damage
        if self.hp <= 0:
            soundMgr.play_sfx("spaceship died")
            if self.stage in [4, 5]:
                # Shatter the eye alien into many glowing flying fragments!
                ShatterEffect.trigger(self, rows=4, cols=4)
            else:
                death_effect = SparksEffect(self)
                death_effect.start()
            self.kill()
