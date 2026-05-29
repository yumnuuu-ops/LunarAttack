"""
This will be made as a class.
It will contain all the effects of the move that will be used on the players.
The boss battle scene itself will take place in another python file.

Upon completion of the boss battle, a message will be shown.
A decision tree might be implemented (taught in data structures).
(Good exercise before proceeding with the real assignment in C++).
"""

import pygame
import math
import random
import cv2
import numpy as np
import os
from AnimationManager import AnimationManager
import utils

# I am gonna be an astrophysician after this
# Am I a computer science student with specialization in Artificial Intelligence
# Or am I a Physician? Hm, I don't know anymore

def loadAsteroidImages():
    folder = os.path.join("Assets", "Asteroids")
    asteroidGroups = {"Fiery": [], "Neutral": [], "Small": []}
    for filename in (os.listdir(folder)):
        img = pygame.image.load(os.path.join(folder, filename)).convert_alpha()
        name = filename.lower()
        if "fiery" in name:
            asteroidGroups["Fiery"].append(img)
        elif "small" in name:
            asteroidGroups["Small"].append(img)
        else:
            asteroidGroups["Neutral"].append(img)
    return asteroidGroups

class Boss:
    max_hp = 60
    phase2_hp = max_hp // 2 # Floor Division, phase 2 will start when HP is 50% or below

    def __init__(self, assetManager, soundManager, screen_w):
        # Initial State
        self.hp = self.max_hp
        self.phase = 1
        self.screen_w = screen_w
        self.alive = True
        self.invincibility = False
        self.radius = 90
        self.speed  = 10 # Need to experiment
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.soundManager = soundManager
        self.assetManager = assetManager
        self.animation_phase1_idle = AnimationManager(assetManager.getAnim("MoonP1"))

        # Phase 2
        self.phase2_transition_animation = False
        self.animation_phase1_phase2_transition = AnimationManager(assetManager.getAnim("MoonP1TP2"))
        self.animation_phase2_idle = AnimationManager(assetManager.getAnim("MoonP2"))

        # Phase 2 Clone
        self.clone_rect = self.rect.copy()
        self.clone_active = False
        self.animation_clone_spawn = AnimationManager(assetManager.getAnim("MoonCSpawn"))
        self.animation_clone_idle = AnimationManager(assetManager.getAnim("MoonC"))

        # Giant State
        self.giant_state = False
        self.giant_state_transition_animation = False
        self.animation_giant_transition = AnimationManager(assetManager.getAnim("MoonP2TG"))
        self.animation_giant_idle = AnimationManager(assetManager.getAnim("MoonG"))

        # Phase 2 Scarred
        self.phase2_scarred = False
        self.phase2_scarred_transition_animation = False
        self.animation_phase2_scarred_transition = AnimationManager(assetManager.getAnim("MoonGTP2Scarred"))
        self.animation_phase2_scarred_idle = AnimationManager(assetManager.getAnim("MoonP2Scarred"))

        # Current Move Used and Asteroids Spawn
        self.attack_highlight = []
        self.asteroids = []
        self.active_masses = []
        self.currentMove = []

        # Define which move can be used in each phase
        # If we want to explain how it can move, let's just say he used domain expansion :D
        self.phase1Move = ["Asteroid Barrage", "Asteroid AOE", "Gravity Pull", "Warp", "Teleportation"]
        self.phase2Move = ["Asteroid Barrage", "Asteroid AOE", "Gravity Pull", "Warp", "Teleportation", "Mass Release"]

        # Movement State:
        self.move_dir = 1  # 1 = right, -1 = left
        self.move_speed = 2
        self.move_left_bound = 200
        self.move_right_bound = self.screen_w - 200
        self.moving = True  # Off During Eclipse Phase (Invincible no need to move)

        # Teleportation
        self.teleport_active = False
        self.teleport_state = None  # "vanish" / "appear" / "barrage" / "break" (what should I call this?)
        self.teleport_timer = 0
        self.teleports_left = 0
        self.teleportCount = 3
        self.teleportBreak = 30

        self.animation_teleport_vanish = AnimationManager(assetManager.getAnim("MoonTeleFastOut"), speed=0.3)
        self.animation_teleport_appear = AnimationManager(assetManager.getAnim("MoonTeleFastIn"), speed=0.3)

    def move(self):
        if not self.moving:
            return
        self.rect.x += self.move_dir * self.move_speed
        if self.rect.left <= self.move_left_bound:
            self.move_dir = 1
        elif self.rect.right >= self.move_right_bound:
            self.move_dir = -1

    def takeDamage(self, n):
        if self.invincibility:
            return
        self.hp -= n
        if self.phase == 1 and self.hp <= self.phase2_hp:
            self.phase = 2  # Triggers phase 2 transition animation
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self):
        if self.teleport_active:
            self.updateTeleport()
            return
        elif self.phase == 3:
            if self.phase2_scarred_transition_animation:
                self.animation_phase2_scarred_idle.update()
            else:
                self.giant_state = False
                self.animation_phase2_scarred_transition.update(loop=False)
                lastFrameTrans = len(self.animation_phase2_scarred_transition.frames) - 1
                if self.animation_phase2_scarred_transition.index >= lastFrameTrans:
                    self.phase2_scarred_transition_animation = True
        elif self.giant_state:
            if self.giant_state_transition_animation:
                self.animation_giant_idle.update()
            else:
                self.clone_active = False
                self.animation_giant_transition.update(loop=False)
                lastFrameTrans = len(self.animation_giant_transition.frames) - 1
                if self.animation_giant_transition.index >= lastFrameTrans:
                    self.giant_state_transition_animation = True
        elif self.phase == 1:
            self.animation_phase1_idle.update()
        elif self.phase == 2:
            self.clone_active = True
            if self.phase2_transition_animation:
                self.animation_phase2_idle.update()
                self.animation_clone_idle.update()
            else:
                self.clone_rect = self.rect.copy()
                self.clone_rect.x = self.clone_rect.x + 300
                self.animation_phase1_phase2_transition.update(loop=False)
                lastFrameTrans = len(self.animation_phase1_phase2_transition.frames) - 1
                self.animation_clone_spawn.update(loop=False)
                lastFrameClone = len(self.animation_clone_spawn.frames) - 1
                if self.animation_phase1_phase2_transition.index >= lastFrameTrans and self.animation_clone_spawn.index >= lastFrameClone:
                    self.phase2_transition_animation = True

    def draw(self, screen):
        frame = None
        frame2 = None
        if self.teleport_active:
            if self.teleport_state == "vanish":
                frame = self.animation_teleport_vanish.get_current_frame()
            elif self.teleport_state == "appear":
                frame = self.animation_teleport_appear.get_current_frame()
            elif self.teleport_state == "pause":
                if self.phase == 2:
                    frame = self.animation_phase2_idle.get_current_frame()
                else:
                    frame = self.animation_phase1_idle.get_current_frame()
        elif self.phase == 3:
            if self.phase2_scarred_transition_animation:
                frame = self.animation_phase2_scarred_idle.get_current_frame()
            else:
                frame = self.animation_phase2_scarred_transition.get_current_frame()
        elif self.giant_state:
            if self.giant_state_transition_animation:
                frame = self.animation_giant_idle.get_current_frame()
            else:
                frame = self.animation_giant_transition.get_current_frame()
        elif self.phase == 1:
            frame = self.animation_phase1_idle.get_current_frame()
        elif self.phase == 2:
            if self.phase2_transition_animation:
                frame = self.animation_phase2_idle.get_current_frame()
                frame2 = self.animation_clone_idle.get_current_frame()
            else:
                frame = self.animation_phase1_phase2_transition.get_current_frame()
                frame2 = self.animation_clone_spawn.get_current_frame()
        if frame:
            draw_rect = frame.get_rect(center=self.rect.center)
            screen.blit(frame, draw_rect)
        if frame2:
            draw_rect = frame2.get_rect(center=self.clone_rect.center)
            screen.blit(frame2, draw_rect)

    def gravityPull(self, player_rect, screen_w, screen_h):
        # Create summonedMass at a location randomly under specified conditions that pulls players in
        mass = Mass(self.assetManager, self.soundManager)
        mass.spawnLocation(player_rect, self.rect, screen_w, screen_h)
        self.active_masses.append(mass)

    def asteroidBarrage(self, player_rect):
        cx, cy = self.rect.center
        aim = math.atan2(player_rect.centery - cy, player_rect.centerx - cx)
        count = random.randint(5, 8)
        spread = math.radians(120)
        if self.phase == 1:
            asteroidType = "Neutral"
        else:
            asteroidType = "Fiery"
        for i in range(count):
            # t is made to even the spread of the asteroids
            t = i / (count - 1)
            angle = aim - spread / 2 + spread * t
            vx = math.cos(angle)
            vy = math.sin(angle)
            size = random.randint(26, 46)
            self.asteroids.append(Asteroid(cx, cy, vx, vy, size, asteroid_type=asteroidType))

    def massRelease(self):
        self.giant_state = True
        self.invincibility = True

    def teleportAttack(self, player_rect, screen_w):
        if self.teleport_active:
            return
        self.teleport_active = True
        self.teleports_left = self.teleportCount
        self.moving = False  # Stop movement during teleportation
        self.invincibility = True
        self.player_rect = player_rect
        self.screen_w = screen_w
        self.beginTeleport()

    def beginTeleport(self):
        self.teleport_state = "vanish"
        self.soundManager.play_sfx("")
        self.teleport_timer = len(self.animation_teleport_vanish.frames)
        self.animation_teleport_vanish.index = 0

    def updateTeleport(self):
        if not self.teleport_active:
            return

        if self.teleport_state == "vanish":
            self.animation_teleport_vanish.update(loop=False)
            if self.animation_teleport_vanish.index >= len(self.animation_teleport_vanish.frames) - 1:
                new_x = random.randint(self.move_left_bound, self.move_right_bound)
                self.rect.centerx = new_x
                self.soundManager.play_sfx("")
                self.teleport_state = "appear"
                self.animation_teleport_appear.index = 0

        elif self.teleport_state == "appear":
            self.animation_teleport_appear.update(loop=False)
            if self.animation_teleport_appear.index >= len(self.animation_teleport_appear.frames) - 1:
                self.asteroidBarrage(self.player_rect)
                self.teleport_state = "break"
                self.teleport_timer = self.teleportBreak

        elif self.teleport_state == "break":
            self.teleport_timer -= 1
            if self.teleport_timer <= 0:
                self.teleports_left -= 1
                if self.teleports_left > 0:
                    self.beginTeleport()
                else:
                    self.endTeleport()

    def endTeleport(self):
        self.teleport_active = False
        self.teleport_state = None
        self.moving = True  # Resume movement
        self.invincibility = False

class Beam:
    def __init__(self, screen_w, screen_h):
        self.waves = 5
        self.beamsPerWave = 10
        self.beamSpeed = 32
        self.spawnBack = 500
        self.breakPerWave = 16
        self.beams = []
        self.asteroids = []
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.active = False

    def BeamStorm(self, asteroid_type, soundManager):
        if self.active == True:
            return
        self.soundManager = soundManager
        self.active = True
        self.asteroid_type = asteroid_type
        self.beamWavesLeft = self.waves
        self.beginTelegraph()

    def beginTelegraph(self):
        self.beamState = "telegraph"
        self.beamTimer = 28
        self.beams = []
        for i in range (self.beamsPerWave):
            px = random.randint(150, self.screen_w - 150)
            py = random.randint(120, self.screen_h - 120)
            angle = random.uniform(0, math.tau)
            self.beams.append(((px, py), (math.cos(angle), math.sin(angle))))

    def asteroidAttack(self, asteroid_type):
        self.beamState = "strike"
        self.beamTimer = self.breakPerWave
        for (px, py), (vx, vy) in self.beams:
            sx = px - vx * self.spawnBack
            sy = py - vy * self.spawnBack
            size = 50
            self.asteroids.append(Asteroid(sx, sy, vx, vy, size, fixed_speed=self.beamSpeed, asteroid_type=asteroid_type))

    def update(self):
        for asteroid in self.asteroids:
            asteroid.move()
        self.asteroids = [asteroid for asteroid in self.asteroids if not asteroid.removeAsteroid(self.screen_w, self.screen_h)]
        if not self.active:
            return
        self.beamTimer -= 1
        if self.beamTimer <= 0:
            if self.beamState == "telegraph":
                self.soundManager.play_sfx("asteroid")
                self.asteroidAttack(self.asteroid_type)
            else:
                self.beamWavesLeft -= 1
                if self.beamWavesLeft > 0:
                    self.beginTelegraph()
                else:
                    self.active = False

    def drawTelegraph(self, screen):
        if self.beamState == "telegraph":
            pulse = abs(math.sin(self.beamTimer * 0.4))
            col = (255, int(50 + 130 * pulse), int(50 * pulse))
            for (px, py), (vx, vy) in self.beams:
                start = (px - vx * 2000, py - vy * 2000)
                end = (px + vx * 2000, py + vy * 2000)
                pygame.draw.line(screen, col, start, end, 3)

class Asteroid:
    asteroidImages = None
    def __init__(self, x, y, vx, vy, size, fixed_speed=None, asteroid_type="Neutral"):
        if self.asteroidImages is None:
            self.asteroidImages = loadAsteroidImages()
        asteroidImage = random.choice(self.asteroidImages[asteroid_type])
        self.image = pygame.transform.scale(asteroidImage, (size, size))
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = random.uniform(0, 360) # Spawns at a random angle
        self.fixed_speed = fixed_speed
        self.speed = self.fixed_speed if fixed_speed else 1.0 # Speed Increases Over Time
        self.size = size
        self.spin = 0
        self.fx = float(x)
        self.fy = float(y)
        self.vx = vx
        self.vy = vy

    def move(self):
        if self.fixed_speed is None:
            self.speed += 0.2
            if self.speed > 15:
                self.speed = 15
        self.fx += self.vx * self.speed
        self.fy += self.vy * self.speed
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)
        self.angle += (self.speed * 2) % 360

    def draw(self, screen):
        rotatedImage = pygame.transform.rotate(self.image, self.angle)
        drawAsteroid = rotatedImage.get_rect(center=self.rect.center)
        screen.blit(rotatedImage, drawAsteroid)

    def removeAsteroid(self, w, h):
        return(self.rect.right < -200 or self.rect.left > w + 200 or
               self.rect.bottom < -200 or self.rect.top > h + 200)

class Mass:
    G = 6.674
    def __init__(self, assetManager, soundManager):
        self.life = 100
        self.radius = 30
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.generatedMass = random.randint(1000, 1500)
        self.soundManager = soundManager
        self.animation = AnimationManager(assetManager.getAnim("Mass"))
        self.animation_spawn = AnimationManager(assetManager.getAnim("MassSpawn"))
        self.animation_despawn = AnimationManager(assetManager.getAnim("MassE"))
        self.animation_spawn_loaded = False
        self.animation_despawn_loaded = False
        self.isDead = False

    def update(self):
        if self.isDead:
            return
        elif self.life <= 0:
            self.animation_despawn.update(loop=False)
            lastFrameTrans = len(self.animation_despawn.frames) - 1
            if self.animation_despawn.index >= lastFrameTrans:
                self.animation_despawn_loaded = True
                self.isDead = True
                self.soundManager.stop_sfx("mass_active")
        elif self.life > 0 and not self.isDead:
            if self.animation_spawn_loaded:
                self.animation.update()
                self.life -= 1
            else:
                self.animation_spawn.update(loop=False)
                lastFrameTrans = len(self.animation_spawn.frames) - 1
                if self.animation_spawn.index >= lastFrameTrans:
                    self.animation_spawn_loaded = True
                    self.soundManager.loop_sfx("mass_active", 0.5)

    def draw(self, screen):
        frame = None
        if self.isDead:
            return
        elif self.life <= 0:
            if self.animation_despawn_loaded:
                return
            else:
                frame = self.animation_despawn.get_current_frame()
        elif self.life > 0 and not self.isDead:
            if self.animation_spawn_loaded:
                frame = self.animation.get_current_frame()
            else:
                frame = self.animation_spawn.get_current_frame()
        if frame:
            draw_rect = frame.get_rect(center=self.rect.center)
            screen.blit(frame, draw_rect)

    def spawnLocation(self, player_rect, moon_rect, screen_w, screen_h, min_dist=200):
        x = random.randint(50, screen_w)
        y = random.randint(50, screen_h)
        if math.hypot(x - player_rect.centerx, y - player_rect.centery) < min_dist and math.hypot(x - moon_rect.centerx, y - moon_rect.centery) < min_dist:
            for i in range(100):
                x = random.randint(50, screen_w - 50)
                y = random.randint(50, screen_h - 50)
                distanceToPlayer = math.hypot(x - player_rect.centerx, y - player_rect.centery)
                distanceToMoon = math.hypot(x - moon_rect.centerx, y - moon_rect.centery)
                if distanceToPlayer >= min_dist and distanceToMoon >= min_dist:
                    self.rect.center = (x, y)
                    return
        self.rect.center = (x, y)
        return

    def gravityPull(self, player_rect, player_mass, falloff):
        cx, cy = self.rect.center
        dx = cx - player_rect.centerx
        dy = cy - player_rect.centery
        # Calculate the distance between player and the moon
        # Will not crash as the distance will not be 0, thus avoiding divide by zero error
        # Done by making collision
        dist = max(40.0, math.hypot(dx, dy))
        # Formula
        # Force = G * ((m1 * m2) / r^2)
        # Game simulation will use min max to control minimum force and maximum force
        # Fall off will be used to control how fast the force dies the further it moves out
        force = self.G * ((player_mass * self.generatedMass) // (dist ** falloff))
        # Ensures force is felt across the screen
        force = max(1.5, force)
        # Ensures force is not overly strong when near
        force = min(6.0, force)
        nx, ny = dx / dist, dy / dist
        pull_x = int(nx * force)
        pull_y = int(ny * force)
        player_rect.x += pull_x
        player_rect.y += pull_y
        return (pull_x, pull_y)