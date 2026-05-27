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

    def __init__(self):
        # Initial State
        self.hp = self.max_hp
        self.phase = 1
        self.alive = True
        self.radius = 90
        self.speed  = 10 # Need to experiment
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)

        # Phase 2
        self.clone_rect = self.rect.copy()
        self.clone_active = False

        # Current Move Used and Asteroids Spawn
        self.attack_highlight = []
        self.asteroids = []
        self.active_masses = []
        self.currentMove = []

        # Define which move can be used in each phase
        # If we want to explain how it can move, let's just say he used domain expansion :D
        self.phase1Move = ["Asteroid Barrage", "Asteroid AOE", "Gravity Pull", "Warp"]
        self.phase2Move = ["Asteroid Barrage", "Asteroid AOE", "Gravity Pull", "Warp", "Teleportation"]

    def update(self):
        # Placeholder for now
        print("Hi")

    def gravityPull(self, player_rect, screen_w, screen_h):
        # Create summonedMass at a location randomly under specified conditions that pulls players in
        mass = Mass()
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
    def BeamStorm(self, asteroid_type):
        if self.active == True:
            return
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
    asteroidImages = loadAsteroidImages()
    def __init__(self, x, y, vx, vy, size, fixed_speed=None, asteroid_type="Neutral"):
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
    def __init__(self):
        self.radius = 30
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.generatedMass = random.randint(1000, 1500)

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