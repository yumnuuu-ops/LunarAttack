import pygame
import random
import math
from enemy.Alien import Alien
from enemy.Formation import Formation
from globals import projectile_group

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
        
        # Groups managed
        self.alien_group = pygame.sprite.Group()
        self.enemy_projectile_group = pygame.sprite.Group()
        
        # Spawning configuration
        self.enemies_spawned_so_far = 0
        self.total_enemies_to_spawn = 0
        
        # Formations setup
        self.last_y = 80
        self.y_spacing = 20
        
        # Setup Grid Slots
        cols_s4 = [((screen_w - 5 * 150) // 2) + i * 150 for i in range(6)]
        self.grid_slots_stage4 = [(col, self.last_y + ((5 - i if i > 2 else i) * self.y_spacing)) for i, col in enumerate(cols_s4)]
        
        cols_s5 = [((screen_w - 7 * 130) // 2) + i * 130 for i in range(7)]
        self.grid_slots_stage5 = []
        # Build second row formation (closest to player - spawns first)
        for i, col in enumerate(cols_s5):
            self.grid_slots_stage5.append((col, 2 * self.last_y + ((6 - i if i > 2 else i) * self.y_spacing)))
        # Build first row formation (further away - spawns second)
        for i, col in enumerate(cols_s5):
            self.grid_slots_stage5.append((col, self.last_y + ((6 - i if i > 2 else i) * self.y_spacing)))
            
        self.formation = Formation(screen_w, screen_h, self.grid_slots_stage4)
        self.alien_types = ["alien_drone", "tendril_alien", "tendril_alien"]

    def setup_stage_config(self, stage):
        self.alien_group.empty()
        self.enemy_projectile_group.empty()
        self.formation.reset()
        
        if stage == STAGE_2:
            self.enemies_spawned_so_far = 2
            self.total_enemies_to_spawn = 20
            p1 = Alien("tendril_alien", 480, 150, stage=2)
            p1.phase = "stationary"
            self.alien_group.add(p1)
            p2 = Alien("tendril_alien", 800, 150, stage=2)
            p2.phase = "stationary"
            self.alien_group.add(p2)
        elif stage == STAGE_3:
            self.enemies_spawned_so_far = 2
            self.total_enemies_to_spawn = 30
            p1 = Alien("tendril_alien", 480, 150, stage=3)
            p1.phase = "stationary"
            self.alien_group.add(p1)
            p2 = Alien("tendril_alien", 800, 150, stage=3)
            p2.phase = "stationary"
            self.alien_group.add(p2)
        elif stage == STAGE_4:
            self.formation = Formation(self.screen_w, self.screen_h, self.grid_slots_stage4)
            self.enemies_spawned_so_far = 0
            self.total_enemies_to_spawn = 18
        elif stage == STAGE_5:
            self.formation = Formation(self.screen_w, self.screen_h, self.grid_slots_stage5)
            self.enemies_spawned_so_far = 0
            self.total_enemies_to_spawn = 36

    def spawn_aliens(self, stage):
        if self.enemies_spawned_so_far >= self.total_enemies_to_spawn:
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
            num_to_spawn = random.choice([3, 4])
            for idx in range(num_to_spawn):
                if self.enemies_spawned_so_far < self.total_enemies_to_spawn:
                    if idx % 2 == 0:
                        spawn_x = -100 # Off-screen left
                    else:
                        spawn_x = 1380 # Off-screen right
                    spawn_y = 60 + (idx * 110)
                    new_alien = Alien("alien_drone", spawn_x, spawn_y, stage=2 if stage == STAGE_2 else 3)
                    self.alien_group.add(new_alien)
                    self.enemies_spawned_so_far += 1
        elif stage in [STAGE_4, STAGE_5]:
            # Spawn in a swarm! Request up to 6 slots (3 pairs) per tick
            slots_to_spawn = []
            for _ in range(3):
                slots_to_spawn.extend(self.formation.get_spawn_slots())
            for idx, slot in enumerate(slots_to_spawn):
                if self.enemies_spawned_so_far < self.total_enemies_to_spawn:
                    if slot[0] < 640:
                        spawn_x = -50 - (idx * 80)
                        spawn_y = 0
                    else:
                        spawn_x = self.screen_w + 50 + (idx * 80)
                        spawn_y = 0
                    alien_type = self.alien_types[1] if stage == STAGE_4 else self.alien_types[2]
                    new_alien = Alien(alien_type, spawn_x, spawn_y, stage=4 if stage == STAGE_4 else 5,
                                      target_x=slot[0], target_y=slot[1])
                    self.alien_group.add(new_alien)
                    self.formation.register_alien(new_alien, slot)
                    self.enemies_spawned_so_far += 1

    def handle_updates_and_collisions(self, stage, player_touching_edge=False):
        # 1. Update enemies and collect enemy bullets
        enemy_bullets = []
        for alien in self.alien_group:
            result = alien.update(player_pos=self.player.rect.center, player_touching_edge=player_touching_edge)
            if result is not None:
                enemy_bullets.append(result)
                # Satisfying micro-shake when enemy shoots
                self.trigger_shake(2, 4)
        self.enemy_projectile_group.add(*enemy_bullets)
        self.enemy_projectile_group.update()

        # 2. Release dead aliens from formation in stages 4 and 5
        if stage in [STAGE_4, STAGE_5]:
            dead_aliens = [alien for alien in self.formation.active_aliens if not alien.alive()]
            for alien in dead_aliens:
                self.formation.release_alien(alien)

        # 3. Bullet hits checking (projectile hits alien)
        ALIEN_POINTS = {"alien_drone": 50, "tendril_alien": 150}
        hits = pygame.sprite.groupcollide(projectile_group, self.alien_group, True, False)
        for bullet, hit_aliens in hits.items():
            for alien in hit_aliens:
                alien.takeDamage(bullet.damage)
                if alien.hp <= 0:
                    self.hud.register_kill(ALIEN_POINTS.get(alien.alien_type, 50))
                    if stage in [STAGE_4, STAGE_5]:
                        self.formation.release_alien(alien)

        # 4. Player-Alien Collision Check (Kamikaze / Crashing into player!)
        if not self.player.invincible:
            collided_aliens = [alien for alien in self.alien_group if self.player.rect.colliderect(alien.rect)]
            for alien in collided_aliens:
                alien.kill()
                self.player.takeDamage(1)
                self.hud.take_damage()
                if stage in [STAGE_4, STAGE_5]:
                    self.formation.release_alien(alien)

        # 5. Player-EnemyBullet Collision Check
        collided_bullets = [bullet for bullet in self.enemy_projectile_group if self.player.rect.colliderect(bullet.rect)]
        for bullet in collided_bullets:
            bullet.kill()

            if not self.player.invincible:
                self.player.takeDamage(1)
                self.hud.take_damage()

    def draw(self, game_surface, stage):
        # Draw bullets and alien group sprites
        self.enemy_projectile_group.draw(game_surface)
        self.alien_group.draw(game_surface)
        
        # Render lock-on visual sights (no red rect debug outlines!)
        for alien in self.alien_group:
            # Draw blinking red Lock-On laser sights only for stationary sentries
            if hasattr(alien, "phase") and alien.phase == "stationary":
                timer = alien.shoot_cooldown
                crit_threshold = 15
                warn_threshold = 40
                
                if timer <= crit_threshold:
                    # Thick solid warning beam pointing directly at the player!
                    pygame.draw.line(game_surface, (255, 0, 0), alien.rect.center, self.player.rect.center, 3)
                else:
                    # Blinks faster as cooldown counts down
                    blink_interval = 8 if timer > warn_threshold else 4
                    if pygame.time.get_ticks() // (blink_interval * 15) % 2 == 0:
                        pygame.draw.line(game_surface, (255, 30, 30), alien.rect.center, self.player.rect.center, 2)
