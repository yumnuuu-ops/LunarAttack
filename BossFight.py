from Boss import Boss, Beam, Mass
from globals import projectile_group, assetMgr, soundMgr
import os
import pygame
from AnimationManager import AnimationManager
from globals import assetMgr, soundMgr


class BossFight:
    moonFolder = os.path.join("Assets", "Moon")

    def __init__(self, screen_w, screen_h, player):
        self.boss = Boss(screen_w, screen_h)
        self.player = player
        self.hud = None
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.boss.rect.center = (screen_w // 2, 160)
        self.beam = None
        self.testKeys = True
        self.finished = False

        self.mode = "intro"
        self.intro_step = "fly_in"
        self.intro_timer = 0
        self.approach_target_y = 450
        self.blackhole = None
        self.fade_alpha = 0
        self.player_speed_backup = player.speed
        self.animation_blackhole = AnimationManager(assetMgr.getAnim("Blackhole"))
        self.animation_blackhole_spawn = AnimationManager(assetMgr.getAnim("BlackholeSpawn"))
        self.animation_blackhole_despawn = AnimationManager(assetMgr.getAnim("BlackholeDespawn"))
        self.blackhole_pos = (self.screen_w // 2, self.screen_h // 2)

        self.player.pos.x = self.screen_w // 2
        self.player.pos.y = self.screen_h + 100
        self.player.rect.x = int(self.player.pos.x)
        self.player.rect.y = int(self.player.pos.y)
        self.fly_in_target_y = self.screen_h - 100
        self.blackhole_spawned = False

    def update(self, events):
        if self.mode == "intro":
            self.updateIntro()
            return
        self.player.update(events)
        self.updateFight(events)

    def updateIntro(self):
        if not getattr(self, '_intro_started', False):
            self._intro_started = True
            self.player.pos.y = self.screen_h + 100
            self.player.rect.y = int(self.player.pos.y)
            self.player.pos.x = self.screen_w // 2
            self.player.rect.x = int(self.player.pos.x)
        self.player.speed = 0

        if self.intro_step == "fly_in":
            if self.player.rect.centery > self.fly_in_target_y:
                self.player.apply_push(0, -4)
                self.player.rect.x = int(self.player.pos.x)
                self.player.rect.y = int(self.player.pos.y)
            else:
                self.intro_step = "blackhole_spawn"
                self.animation_blackhole_spawn.index = 0
                soundMgr.play_sfx("mass spawn")

        elif self.intro_step == "blackhole_spawn":
            self.animation_blackhole_spawn.update(loop=False)
            last = len(self.animation_blackhole_spawn.frames) - 1
            if self.animation_blackhole_spawn.index >= last:
                self.intro_step = "blackhole"
                self.intro_timer = 120
                soundMgr.loop_sfx("mass active", 0.5)

        elif self.intro_step == "blackhole":
            self.intro_timer -= 1
            self.animation_blackhole.update()
            bx, by = self.blackhole_pos
            dx = bx - self.player.rect.centerx
            dy = by - self.player.rect.centery
            dist = max(20.0, (dx * dx + dy * dy) ** 0.5)
            self.player.apply_push(dx / dist * 7, dy / dist * 7)
            self.player.rect.x = int(self.player.pos.x)
            self.player.rect.y = int(self.player.pos.y)
            if self.intro_timer <= 0:
                self.intro_step = "descend"
                self.intro_timer = 50

        elif self.intro_step == "descend":
            self.intro_timer -= 1
            self.animation_blackhole.update()
            self.boss.rect.centery += 4
            if self.intro_timer <= 0:
                self.intro_step = "blackout"

        elif self.intro_step == "blackout":
            self.fade_alpha += 8
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                soundMgr.stop_sfx("mass active")
                self.startFight()

    def startFight(self):
        soundMgr.stop_sfx("mass active")
        self.mode = "fight"
        self.player.speed = self.player_speed_backup
        self.boss.rect.center = (self.screen_w // 2, 160)
        self.blackhole = None
        self.player.pos.x = self.screen_w // 2
        self.player.pos.y = self.screen_h - 150
        self.player.rect.x = int(self.player.pos.x)
        self.player.rect.y = int(self.player.pos.y)

    def updateFight(self, events):
        if self.testKeys:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        soundMgr.play_sfx("asteroid")
                        self.boss.asteroidBarrage(self.player.rect)
                    elif event.key == pygame.K_2:
                        self.boss.gravityPull(self.player.rect,
                                              self.screen_w, self.screen_h)
                    elif event.key == pygame.K_3:
                        if self.beam is None or not self.beam.active:
                            self.beam = Beam(self.screen_w, self.screen_h)
                            asteroid_type = "Neutral" if self.boss.phase == 1 else "Fiery"
                            self.beam.BeamStorm(asteroid_type)
                    elif event.key == pygame.K_p:
                        self.boss.phase = 2 if self.boss.phase == 1 else 1
                        if self.boss.phase == 1:
                            self.boss.phase2_transition_animation = False
                    elif event.key == pygame.K_g:
                        self.boss.massRelease()
                    elif event.key == pygame.K_u:
                        self.boss.phase = 3
                    elif event.key == pygame.K_4:
                        self.boss.teleportAttack(self.player.rect, self.screen_w, self.screen_h)
                    elif event.key == pygame.K_5:
                        self.boss.swapWithClone(self.player.rect)
                    elif event.key == pygame.K_6:
                        self.boss.cloneMass(self.player.rect)

        self.boss.update(self.player.rect)
        self.boss.move()
        self.boss.moveClone()
        self.boss.chooseMove(self.player.rect)

        for projectile in projectile_group:
            if projectile.rect.colliderect(self.boss.rect):
                if getattr(projectile, "is_explosion", False):
                    if self.boss not in projectile.damaged_enemies:
                        self.boss.takeDamage(projectile.damage)
                        projectile.damaged_enemies.add(self.boss)
                    continue
                if hasattr(projectile, "ExplosiveProjectile") and projectile.selectedProj in projectile.ExplosiveProjectile:
                    self.boss.takeDamage(projectile.damage)
                    projectile.detonate()
                else:
                    self.boss.takeDamage(projectile.damage)
                    projectile.kill()

        for asteroid in self.boss.asteroids:
            asteroid.move()
            self.checkAsteroidHits()
        self.boss.asteroids = [asteroid for asteroid in self.boss.asteroids
                               if not asteroid.removeAsteroid(self.screen_w, self.screen_h)]

        for asteroid in self.boss.clone_asteroids:
            asteroid.move()
        self.boss.clone_asteroids = [asteroid for asteroid in self.boss.clone_asteroids
                                     if not asteroid.removeAsteroid(self.screen_w, self.screen_h)]

        for mass in self.boss.active_masses:
            mass.update()
            mass.gravityPull(self.player.rect, 5, 1.5)
        self.player.pos.x = self.player.rect.x
        self.player.pos.y = self.player.rect.y

        if self.beam is not None:
            self.beam.update()
            self.checkAsteroidHits()

        if not self.boss.alive:
            self.finished = True

    def checkAsteroidHits(self):
        if self.player.invincible:
            return

        for asteroid in self.boss.asteroids[:]:
            if pygame.sprite.collide_mask(self.player, asteroid):
                self.player.takeDamage(1)
                self.hud.take_damage()
                self.boss.asteroids.remove(asteroid)
        if self.beam is not None:
            for asteroid in self.beam.asteroids[:]:
                if pygame.sprite.collide_mask(self.player, asteroid):
                    self.player.takeDamage(1)
                    self.hud.take_damage()
                    self.beam.asteroids.remove(asteroid)

    def draw(self, screen):
        self.boss.draw(screen)

        if self.blackhole is not None:
            self.blackhole.draw(screen)

        for mass in self.boss.active_masses:
            if not mass.isDead:
                mass.draw(screen)
            else:
                self.boss.active_masses.remove(mass)

        for asteroid in self.boss.asteroids:
            asteroid.draw(screen)

        for asteroid in self.boss.clone_asteroids:
            asteroid.draw(screen)

        if self.beam is not None:
            self.beam.drawTelegraph(screen)
            for asteroid in self.beam.asteroids:
                asteroid.draw(screen)

        if self.mode == "intro":
            if self.intro_step == "blackhole_spawn":
                frame = self.animation_blackhole_spawn.get_current_frame()
            elif self.intro_step in ("blackhole", "descend"):
                frame = self.animation_blackhole.get_current_frame()
            else:
                frame = None
            if frame:
                screen.blit(frame, frame.get_rect(center=self.blackhole_pos))