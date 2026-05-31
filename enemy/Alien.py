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
        self.stage = stage

        self.rect = self.image.get_rect()
        y = -100 if self.stage == 1 else y
        self.pos = pygame.math.Vector2(x, y)
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        self.target_x = target_x
        self.target_y = target_y
        
        #for shielding pulse effect
        self.time_alive = 0.0 
        
        # for portal effect variables
        self.portal_age = 0
        self.enemy_alpha = 255
        self.enemy_scale = 1.0
        self.particles = []
        self.spawned_particles = False
        self.target_lock_sfx_played = False
        
        # default cooldown
        self.shoot_cooldown = random.randint(60, 180)
        if stage == 4:
            self.shoot_cooldown = random.randint(240, 480)
        elif stage == 5:
            self.shoot_cooldown = random.randint(180, 360)

        if target_x is not None and target_y is not None:
            if stage in [4, 5]:
                self.phase = "spawning_portal"
                self.enemy_alpha = 0
                self.enemy_scale = 0.65
            else:
                self.phase = "entering"
        else:
            if stage in [2, 3]:
                self.phase = "stage2_align"
                self.target_y = y
                self.align_timer = random.randint(60, 100)
                self.dive_vx = 0
                self.dive_vy = 0
            else:
                self.phase = "sine_wave_plane_moving"
        
        # stats based on current Stage
        if stage == 1:
            self.hp = 50
            self.speed = 2
        elif stage in [2, 3]:
            self.hp = 60
            self.speed = 3 if stage == 2 else 4
        elif stage in [4, 5]:
            self.hp = 55
            self.speed = 3 if stage == 4 else 4
        
        self.max_hp = self.hp

        # stats based on enemy type
        if self.alien_type == "tendril_alien":
            self.shield_hp = max(1, int(self.hp * 1.00))
        else:
            self.shield_hp = 0
        
        # variables for zig-zag movement/sine wave pattern
        self.spawn_x = x
        self.wave_time = 10
        self.wave_speed = 0.05
        self.wave_amplitude = 100

    def update(self, player_pos=None, player_touching_edge=False):
        self.animator.update()
        self.image = self.animator.get_current_frame()
        fired_bullet = None

        # calculation code (movement, damage, rotate and etc.)
        if self.phase == "sine_wave_plane_moving": #stage 1
            current_speed = self.speed
            
            self.pos.y += current_speed
            self.wave_time += self.wave_speed
            self.pos.x = self.spawn_x + (self.wave_amplitude * math.sin(self.wave_time))

        elif self.phase == "stationary":# stage 2 & 3 
            # idle hover effect
            self.wave_time += 0.2
            self.pos.y = self.target_y + math.sin(self.wave_time) * 1

            # laser sound effect
            self.shoot_cooldown -= 1
            warn_threshold = 40
            if self.shoot_cooldown <= warn_threshold and not self.target_lock_sfx_played:
                sfx_name = "target lock boosted" if player_touching_edge else ("target lock stage 3" if self.stage == 3 else "target lock stage 2")
                soundMgr.play_sfx(sfx_name)
                self.target_lock_sfx_played = True
            elif self.shoot_cooldown > warn_threshold:
                self.target_lock_sfx_played = False

            if self.shoot_cooldown <= 0:
                self.shoot_cooldown = random.randint(60, 150)

        elif self.phase == "stage2_align": # stage 2 & 3 (aligning to player position)
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

        elif self.phase == "stage2_dive": # stage 2 & 3 (crashing to player)
            current_speed = self.speed
            if player_touching_edge:
                current_speed = self.speed * 2.5
            
            self.pos.x += self.dive_vx * current_speed * 2.8
            self.pos.y += self.dive_vy * current_speed * 2.8

        elif self.phase == "spawning_portal": #stage 4 and 5 (spawning portal effects)
            self.portal_age += 1
            progress = min(1.0, self.portal_age / 45)
            self.enemy_alpha = min(255, self.portal_age * 7)
            self.enemy_scale = 0.65 + progress * 0.35
            
            if self.portal_age >= 45:
                self.phase = "entering"
                self.enemy_alpha = 255
                self.enemy_scale = 1.0
                self.spawn_x = self.pos.x

        elif self.phase == "entering": # stage 4 and 5 (flying to formation slot)
            if abs(self.pos.x - self.target_x) > self.speed:
                if self.pos.x < self.target_x:
                    self.pos.x += self.speed
                else:
                    self.pos.x -= self.speed
                
                # sinusoidal wave entry path
                dist_x = abs(self.pos.x - self.target_x)
                total_dist = abs(self.spawn_x - self.target_x)
                if total_dist == 0:
                    total_dist = 1
                dampener = dist_x / total_dist
                
                self.pos.y = self.target_y + math.sin(self.pos.x * 0.015) * 100 * dampener
            else:
                self.pos.x = self.target_x
                self.pos.y = self.target_y
                self.phase = "in_formation"

        elif self.phase == "in_formation": # stage 4 and 5 (enemies start shooting)
            # idle hover effects
            self.wave_time += 0.2
            self.pos.y = self.target_y + math.sin(self.wave_time) * 2

            # shooting logic
            self.shoot_cooldown -= 1
            if self.shoot_cooldown <= 0:
                if self.stage == 4:
                    self.shoot_cooldown = random.randint(240, 480)
                else:
                    self.shoot_cooldown = random.randint(180, 360)
                self.rect.x = int(self.pos.x)
                self.rect.y = int(self.pos.y)
                fired_bullet = self.shoot(player_pos)

        # calculation for drawing/rendering
        raw_image = self.animator.get_current_frame()
        if self.phase == "stage2_align":
            # set targeting direction for crashing
            self.image = pygame.Surface((0, 0), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        else:
            tight_box = raw_image.get_bounding_rect()
            base_image = raw_image.subsurface(tight_box)

            # create shield effect for stationary
            if self.shield_hp > 0: #stage 2 and 3 only
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
            
            # add rotation effects for plane
            if self.phase == "stage2_dive":
                deg = math.degrees(math.atan2(self.dive_vy, self.dive_vx))
                rotation_angle = 90.0 - deg
                rotated_img = pygame.transform.rotate(self.image, rotation_angle)
                
                tight_rotated_box = rotated_img.get_bounding_rect()
                self.image = rotated_img.subsurface(tight_rotated_box)
                
            # draw portal effects for stage 4 & 5
            if self.phase == "spawning_portal":
                w, h = self.image.get_size()
                new_w = max(1, int(w * self.enemy_scale))
                new_h = max(1, int(h * self.enemy_scale))
                self.image = pygame.transform.smoothscale(self.image, (new_w, new_h))
                self.image.set_alpha(max(0, min(255, int(self.enemy_alpha))))
                
            self.rect = self.image.get_rect()
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # cleanup if it goes off bottom of screen
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
        # check if alien has shield
        if self.shield_hp > 0:
            self.shield_hp -= damage
            if self.shield_hp <= 0:
                soundMgr.play_sfx("shield break")
            return
            
        self.hp -= damage
        if self.hp <= 0:
            soundMgr.play_sfx("spaceship died")
            if self.stage in [4, 5]:
                ShatterEffect.trigger(self, rows=4, cols=4)
            else:
                death_effect = SparksEffect(self)
                death_effect.play_effects()
            self.kill()
