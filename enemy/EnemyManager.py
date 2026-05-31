import pygame
import random
import math
from enemy.Alien import Alien
from enemy.Formation import Formation
from globals import projectile_group, soundMgr

STAGE_1 = "stage_1"
STAGE_2 = "stage_2"
STAGE_3 = "stage_3"
STAGE_4 = "stage_4"
STAGE_5 = "stage_5"

class EnemyManager:
    def __init__(self, player, hud, screen_w, screen_h, trigger_shake_func):
        self.player = player
        self.hud = hud
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.trigger_shake = trigger_shake_func
        
        self.alien_group = pygame.sprite.Group()
        self.enemy_projectile_group = pygame.sprite.Group()
        
        self.enemies_spawned_so_far = 0
        self.total_enemies_to_spawn = 0
        
        #sentry tracking for stage 2 and 3
        self.sentry_left = None
        self.sentry_right = None
        

        #formations for stage 4 & 5
        self.last_y = 80
        self.y_spacing = 20

        cols_s4 = [((screen_w - 5 * 150) // 2) + i * 150 for i in range(6)]
        self.grid_slots_stage4 = [(col, self.last_y + ((5 - i if i > 2 else i) * self.y_spacing)) for i, col in enumerate(cols_s4)]
        
        cols_s5 = [((screen_w - 7 * 130) // 2) + i * 130 for i in range(7)]
        self.grid_slots_stage5 = []

        #second row formation (closest to player&spawns first)
        for i, col in enumerate(cols_s5):
            self.grid_slots_stage5.append((col, 2 * self.last_y + ((6 - i if i > 2 else i) * self.y_spacing)))
        #first row formation
        for i, col in enumerate(cols_s5):
            self.grid_slots_stage5.append((col, self.last_y + ((6 - i if i > 2 else i) * self.y_spacing)))
            
        
        self.formation = Formation(screen_w, screen_h, self.grid_slots_stage4)
        self.alien_types = ["alien_drone", "tendril_alien", "eye_spawn"]



    def setup_stage_config(self, stage):
        self.alien_group.empty()
        self.enemy_projectile_group.empty()
        self.formation.reset()
        self.sentry_left = None
        self.sentry_right = None
        
        if stage == STAGE_2:
            self.enemies_spawned_so_far = 2
            self.total_enemies_to_spawn = 40 
            p1 = Alien("tendril_alien", 480, 150, stage=2)
            p1.phase = "stationary"
            self.alien_group.add(p1)
            p2 = Alien("tendril_alien", 800, 150, stage=2)
            p2.phase = "stationary"
            self.alien_group.add(p2)
            self.sentry_left = p1
            self.sentry_right = p2
        elif stage == STAGE_3:
            self.enemies_spawned_so_far = 2
            self.total_enemies_to_spawn = 60 
            p1 = Alien("tendril_alien", 480, 150, stage=3)
            p1.phase = "stationary"
            self.alien_group.add(p1)
            p2 = Alien("tendril_alien", 800, 150, stage=3)
            p2.phase = "stationary"
            self.alien_group.add(p2)
            self.sentry_left = p1
            self.sentry_right = p2
        elif stage == STAGE_4:
            self.formation = Formation(self.screen_w, self.screen_h, self.grid_slots_stage4)
            self.enemies_spawned_so_far = 0
            self.total_enemies_to_spawn = 18
        elif stage == STAGE_5:
            self.formation = Formation(self.screen_w, self.screen_h, self.grid_slots_stage5)
            self.enemies_spawned_so_far = 0
            self.total_enemies_to_spawn = 36

    def spawn_aliens(self, stage):
        # Stage 2 and 3 spawn drones infinitely until the stationary sentries are destroyed
        if stage not in [STAGE_2, STAGE_3] and self.enemies_spawned_so_far >= self.total_enemies_to_spawn:
            return

        if stage == STAGE_1:
            num_to_spawn = random.randint(2, 3)
            chosen_xs = []
            existing_xs = [a.pos.x for a in self.alien_group if a.pos.y < 150]
            for _ in range(num_to_spawn):
                if self.enemies_spawned_so_far < self.total_enemies_to_spawn:
                    valid_x = None
                    for _ in range(20):
                        candidate_x = random.randint(100, 1180)
                        too_close = False
                        for cx in chosen_xs:
                            if abs(candidate_x - cx) < 160:
                                too_close = True
                                break
                        for ex in existing_xs:
                            if abs(candidate_x - ex) < 160:
                                too_close = True
                                break
                        if not too_close:
                            valid_x = candidate_x
                            break
                    if valid_x is None:
                        valid_x = random.randint(100, 1180)
                    chosen_xs.append(valid_x)
                    new_alien = Alien("alien_drone", valid_x, -100, stage=1)
                    self.alien_group.add(new_alien)
                    self.enemies_spawned_so_far += 1
        elif stage in [STAGE_2, STAGE_3]:
            left_alive = self.sentry_left and self.sentry_left.alive()
            right_alive = self.sentry_right and self.sentry_right.alive()
            
            valid_sides = []
            if left_alive: valid_sides.append("left")
            if right_alive: valid_sides.append("right")
            
            if not valid_sides:
                self.enemies_spawned_so_far = self.total_enemies_to_spawn
                return
                
            num_to_spawn = random.choice([2, 3])
            for idx in range(num_to_spawn):
                side = random.choice(valid_sides)
                if side == "left":
                    spawn_x = -100 # Off-screen left
                else:
                    spawn_x = 1380 # Off-screen right
                spawn_y = 60 + (idx * 110)
                new_alien = Alien("alien_drone", spawn_x, spawn_y, stage=2 if stage == STAGE_2 else 3)
                self.alien_group.add(new_alien)
                self.enemies_spawned_so_far += 1
        elif stage in [STAGE_4, STAGE_5]:
            # get 2 slots for left and right side
            slots_to_spawn = self.formation.get_spawn_slots()
            spawned_any = False
            for idx, slot in enumerate(slots_to_spawn):
                if self.enemies_spawned_so_far < self.total_enemies_to_spawn:
                    # center position
                    spawn_x = 640
                    spawn_y = 150
                    alien_type = self.alien_types[2] 
                    new_alien = Alien(alien_type, spawn_x, spawn_y, stage=4 if stage == STAGE_4 else 5,
                                      target_x=slot[0], target_y=slot[1])
                    
                    self.alien_group.add(new_alien)
                    self.formation.register_alien(new_alien, slot)
                    self.enemies_spawned_so_far += 1
                    spawned_any = True
            
            if spawned_any:
                soundMgr.play_sfx("portal warp")

    def handle_updates_and_collisions(self, stage, player_touching_edge=False):
        # Update enemies and collect enemy bullets
        enemy_bullets = []
        for alien in self.alien_group:
            result = alien.update(player_pos=self.player.rect.center, player_touching_edge=player_touching_edge)
            if result is not None:
                enemy_bullets.append(result)


        self.enemy_projectile_group.add(*enemy_bullets)
        self.enemy_projectile_group.update()

        # Resolve collisions/overlaps between Stage 1 aliens to prevent them from colliding/overlapping
        if stage == STAGE_1:
            aliens = list(self.alien_group)
            for i in range(len(aliens)):
                for j in range(i + 1, len(aliens)):
                    a1 = aliens[i]
                    a2 = aliens[j]
                    
                    dx = a1.pos.x - a2.pos.x
                    dy = a1.pos.y - a2.pos.y
                    dist = math.hypot(dx, dy)
                    min_dist = 90  # Keep them beautifully spaced
                    
                    if dist < min_dist:
                        if dist == 0:
                            dx = random.choice([-1, 1])
                            dy = random.choice([-1, 1])
                            dist = math.hypot(dx, dy)
                        
                        # Calculate push vector
                        push_x = (dx / dist) * (min_dist - dist) * 0.5
                        push_y = (dy / dist) * (min_dist - dist) * 0.5
                        
                        # Apply push
                        a1.pos.x += push_x
                        a1.pos.y += push_y
                        a2.pos.x -= push_x
                        a2.pos.y -= push_y
                        
                        # Update spawn_x so the lateral sine movement trajectory shift persists
                        a1.spawn_x += push_x
                        a2.spawn_x -= push_x
                        
                        # Sync rect immediately
                        a1.rect.center = (int(a1.pos.x), int(a1.pos.y))
                        a2.rect.center = (int(a2.pos.x), int(a2.pos.y))

        # Release dead aliens from formation in stages 4 and 5
        if stage in [STAGE_4, STAGE_5]:
            dead_aliens = [alien for alien in self.formation.active_aliens if not alien.alive()]
            for alien in dead_aliens:
                self.formation.release_alien(alien)

        # Bullet hits checking (projectile hits alien)
        ALIEN_POINTS = {"alien_drone": 50, "tendril_alien": 150}
        hits = pygame.sprite.groupcollide(projectile_group, self.alien_group, False, False)
        for bullet, hit_aliens in hits.items():
            if getattr(bullet, "is_explosion", False):      # Explosion
                for alien in hit_aliens:
                    if alien not in bullet.damaged_enemies: # Can only be damaged once by explosion splash damage
                        alien.takeDamage(bullet.damage)
                        bullet.damaged_enemies.add(alien)

                        if alien.hp <= 0:
                            self.hud.register_kill(ALIEN_POINTS.get(alien.alien_type, 50))
                            if stage in [STAGE_4, STAGE_5]:
                                self.formation.release_alien(alien)
                continue
            if hasattr(bullet, "ExplosiveProjectile") and bullet.selectedProj in bullet.ExplosiveProjectile:    # Detonating the explosive bullet
                bullet.detonate()
            else:
                bullet.kill()   # Normaling projectile

            for alien in hit_aliens:
                alien.takeDamage(bullet.damage)
                if alien.hp <= 0:
                    self.hud.register_kill(ALIEN_POINTS.get(alien.alien_type, 50))
                    if stage in [STAGE_4, STAGE_5]:
                        self.formation.release_alien(alien)

        # Player-Alien Collision Check (Kamikaze / Crashing into player!)
        if not self.player.invincible:
            collided_aliens = [alien for alien in self.alien_group if self.player.rect.colliderect(alien.rect) and getattr(alien, "phase", "") not in ["spawning_portal", "dissolving"]]
            for alien in collided_aliens:
                alien.kill()
                self.player.takeDamage(1)
                self.hud.take_damage()
                if stage in [STAGE_4, STAGE_5]:
                    self.formation.release_alien(alien)

        # Player-EnemyBullet Collision Check
        collided_bullets = [bullet for bullet in self.enemy_projectile_group if self.player.rect.colliderect(bullet.rect)]
        for bullet in collided_bullets:
            bullet.kill()

            if not self.player.invincible:
                self.player.takeDamage(1)
                self.hud.take_damage()

    def draw(self, game_surface, stage):
        self.enemy_projectile_group.draw(game_surface)
        self.alien_group.draw(game_surface)
        
        # render portals and dissolve effects
        portal_positions = set() # (x, y, age)
        for alien in self.alien_group:
            p = getattr(alien, "phase", "")
            if p == "spawning_portal":
                portal_positions.add((alien.rect.centerx, alien.rect.centery, getattr(alien, "portal_age", 0)))
                
        for px, py, age in portal_positions:
            progress = min(1.0, age / 45)
            radius = int(18 + progress * 56)
            alpha = int(220 * (1 - progress))

            portal = pygame.Surface((150, 150), pygame.SRCALPHA)
            center = (75, 75)
            pygame.draw.circle(portal, (190, 40, 255, alpha), center, radius, 4)
            pygame.draw.circle(portal, (255, 70, 120, int(alpha * 0.8)), center, max(4, radius - 12), 3)
            pygame.draw.circle(portal, (80, 10, 130, int(alpha * 0.35)), center, max(1, radius - 22))
            game_surface.blit(portal, portal.get_rect(center=(px, py)))
            
        # render lock-on visual laser
        for alien in self.alien_group:
            if hasattr(alien, "phase") and alien.phase == "stationary":
                timer = alien.shoot_cooldown
                crit_threshold = 15
                warn_threshold = 40
                
                if timer <= crit_threshold:
                    # solid warning beam
                    pygame.draw.line(game_surface, (255, 0, 0), alien.rect.center, self.player.rect.center, 3)
                else:
                    # blink faster as cooldown counts down
                    blink_interval = 8 if timer > warn_threshold else 4
                    if pygame.time.get_ticks() // (blink_interval * 15) % 2 == 0:
                        pygame.draw.line(game_surface, (255, 30, 30), alien.rect.center, self.player.rect.center, 2)
