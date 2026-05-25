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
        self.currentMove = []

        # Define which move can be used in each phase
        self.phase1Move = ["Asteroid Barrage", "Asteroid AOE", "Gravity Pull", "Warp"]
        self.phase2Move = ["Asteroid Barrage", "Asteroid AOE", "Gravity Pull", "Warp", "Teleportation"]