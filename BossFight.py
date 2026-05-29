from Boss import Boss, Beam, Mass
from globals import projectile_group, assetMgr, soundMgr
import os
import pygame


class BossFight:
    moonFolder = os.path.join("Assets", "Moon")

    def __init__(self, screen_w, screen_h, player):
        self.boss = Boss(screen_w)
        self.player = player
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.boss.rect.center = (screen_w // 2, 160)
        self.beam = None
        self.testKeys = True
        self.finished = False

        self.mode = "intro"
        self.intro_step = "approach"
        self.intro_timer = 0
        self.approach_target_y = 450
        self.blackhole = None
        self.fade_alpha = 0
        self.player_speed_backup = player.speed

    def update(self, events):
        if self.mode == "intro":
            self.updateIntro()
            return
        self.player.update()
        self.updateFight(events)

    def updateIntro(self):
        self.player.speed = 0

        if self.intro_step == "approach":
            if self.player.rect.centery > self.approach_target_y:
                self.player.apply_push(0, -5)
                self.player.rect.x = int(self.player.pos.x)
                self.player.rect.y = int(self.player.pos.y)
            else:
                self.intro_step = "blackhole"
                self.intro_timer = 120
                self.blackhole = Mass()
                self.blackhole.rect.center = self.boss.rect.center # Reposition to screen center later
                self.blackhole.generatedMass = 5000

        elif self.intro_step == "blackhole":
            self.intro_timer -= 1
            self.blackhole.update()
            dx = self.blackhole.rect.centerx - self.player.rect.centerx
            dy = self.blackhole.rect.centery - self.player.rect.centery
            dist = max(20.0, (dx * dx + dy * dy) ** 0.5)
            self.player.apply_push(dx / dist * 7, dy / dist * 7)
            self.player.rect.x = int(self.player.pos.x)
            self.player.rect.y = int(self.player.pos.y)
            if self.intro_timer <= 0:
                self.intro_step = "descend"
                self.intro_timer = 50

        elif self.intro_step == "descend":
            self.intro_timer -= 1
            self.boss.rect.centery += 4
            if self.intro_timer <= 0:
                self.intro_step = "blackout"

        elif self.intro_step == "blackout":
            self.fade_alpha += 8
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self._startFight()

    def _startFight(self):
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
                        self.boss.teleportAttack(self.player.rect, self.screen_w)

        self.boss.update()
        self.boss.move()

        for projectile in projectile_group:
            if projectile.rect.colliderect(self.boss.rect):
                self.boss.takeDamage(projectile.damage)
                projectile.kill()

        for asteroid in self.boss.asteroids:
            asteroid.move()
        self.boss.asteroids = [asteroid for asteroid in self.boss.asteroids
                               if not asteroid.removeAsteroid(self.screen_w, self.screen_h)]

        for mass in self.boss.active_masses:
            mass.update()
            mass.gravityPull(self.player.rect, 5, 1.5)
        self.player.pos.x = self.player.rect.x
        self.player.pos.y = self.player.rect.y

        if self.beam is not None:
            self.beam.update()

        if not self.boss.alive:
            self.finished = True

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

        if self.beam is not None:
            self.beam.drawTelegraph(screen)
            for asteroid in self.beam.asteroids:
                asteroid.draw(screen)

        if self.mode == "intro" and self.fade_alpha > 0:
            overlay = pygame.Surface((self.screen_w, self.screen_h))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(self.fade_alpha)
            screen.blit(overlay, (0, 0))