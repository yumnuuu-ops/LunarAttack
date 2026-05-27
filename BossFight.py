from Boss import Boss, Beam, Mass
import os
import pygame

class BossFight:
    # FUTURE IMPROVEMENTS
    # Cutscene where players move in on the corrupted moon. The moon will summon a massive blackhole
    # The blackhole will sucks in players and then the moon will go in later.
    # The boss fight will then start
    moonFolder = os.path.join("Assets", "Moon")
    def __init__(self, screen_w, screen_h, assetManager, player):
        self.boss = Boss(assetManager)
        self.player = player
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.assetManager = assetManager
        for filename in ["moon_phase1", "moon_phase2", "moon_giant"]:
            assetManager.loadTexture(filename, os.path.join(self.moonFolder, filename + ".png"))
        self.boss.rect.center = (screen_w // 2, 160)
        self.beam = None

        # For testing purposes, the attack will be implemented via a decision tree at a later date
        self.testKeys = True

    def loadMoonTexture(self):
        if self.boss.giant_state:
            return self.assetManager.getTexture("moon_giant")
        elif self.boss.phase == 1:
            return self.assetManager.getTexture("moon_phase1")
        else:
            return self.assetManager.getTexture("moon_phase2")

    def update(self, events):
        if self.testKeys:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
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

        # Boss Giant Form
        # Placeholder for future testing

        if not self.boss.alive:
            self.finished = True

    def draw(self, screen):
        moon_img = self.loadMoonTexture()
        if moon_img:
            screen.blit(moon_img, moon_img.get_rect(center=self.boss.rect.center))

        for mass in self.boss.active_masses:
            mass.draw(screen)

        for asteroid in self.boss.asteroids:
            asteroid.draw(screen)

        if self.beam is not None:
            self.beam.drawTelegraph(screen)
            for asteroid in self.beam.asteroids:
                asteroid.draw(screen)