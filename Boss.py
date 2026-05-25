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


# I am gonna be an astrophysician after this
# Am I a computer science student with specialization in Artificial Intelligence
# Or am I a Physician? Hm, I don't know anymore

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
        self.asteroids = []
        self.active_masses = []
        self.currentMove = []

        # Define which move can be used in each phase
        self.phase1Move = ["Asteroid Barrage", "Asteroid AOE", "Gravity Pull", "Warp"]
        self.phase2Move = ["Asteroid Barrage", "Asteroid AOE", "Gravity Pull", "Warp", "Teleportation"]

    def update(self):
        # Placeholder for now
        print("Hi")

    def gravityPull(self, player_rect, screen_w, screen_h):
        print("Hi")
        # Create summonedMass at a location randomly under specified conditions that pulls players in
        mass = summonedMass()
        mass.spawnLocation(player_rect, self.rect, screen_w, screen_h)
        self.active_masses.append(mass)

class summonedMass:
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
        dist = math.hypot(dx, dy)
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