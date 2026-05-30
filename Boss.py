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
from globals import assetMgr, soundMgr
from AnimationManager import AnimationManager


# I am gonna be an astrophysician after this
# Am I a computer science student with specialization in Artificial Intelligence
# Or am I a Physician? Hm, I don't know anymore

def loadAsteroidImages():
    folderPhase1 = os.path.join("Assets", "Asteroids", "phase 1")
    folderPhase2 = os.path.join("Assets", "Asteroids", "phase 2")
    folderClone = os.path.join("Assets", "Asteroids", "quantum moon")
    folderEclipse = os.path.join("Assets", "Asteroids", "eclipse")
    folderScarred = os.path.join("Assets", "Asteroids", "scarred")
    asteroidGroups = {"Scarred": [], "Eclipse": [], "Fiery": [], "Clone": [], "Neutral": [], "Small": []}
    for filename in (os.listdir(folderPhase1)):
        img = pygame.image.load(os.path.join(folderPhase1, filename)).convert_alpha()
        name = filename.lower()
        if "small" in name:
            asteroidGroups["Small"].append(img)
        else:
            asteroidGroups["Neutral"].append(img)
    for filename in (os.listdir(folderPhase2)):
        img = pygame.image.load(os.path.join(folderPhase2, filename)).convert_alpha()
        asteroidGroups["Fiery"].append(img)
    for filename in (os.listdir(folderClone)):
        img = pygame.image.load(os.path.join(folderClone, filename)).convert_alpha()
        asteroidGroups["Clone"].append(img)
    for filename in (os.listdir(folderEclipse)):
        img = pygame.image.load(os.path.join(folderEclipse, filename)).convert_alpha()
        asteroidGroups["Eclipse"].append(img)
    for filename in (os.listdir(folderScarred)):
        img = pygame.image.load(os.path.join(folderScarred, filename)).convert_alpha()
        asteroidGroups["Scarred"].append(img)
    return asteroidGroups

class Boss:
    max_hp = 10000
    phase2_hp = max_hp // 2 # Floor Division, phase 2 will start when HP is 50% or below
    giant_hp = round(max_hp * 0.3)

    def __init__(self, screen_w, screen_h):
        # Initial State
        self.hp = self.max_hp
        self.phase = 1
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.alive = True
        self.invincibility = False
        self.radius = 90
        self.speed  = 10 # Need to experiment
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.animation_phase1_idle = AnimationManager(assetMgr.getAnim("MoonP1"))

        # Phase 2
        self.phase2_transition_animation = False
        self.animation_phase1_phase2_transition = AnimationManager(assetMgr.getAnim("MoonP1TP2"))
        self.animation_phase2_idle = AnimationManager(assetMgr.getAnim("MoonP2"))

        # Phase 2 Clone
        self.clone_rect = self.rect.copy()
        self.clone_active = False
        self.animation_clone_spawn = AnimationManager(assetMgr.getAnim("MoonCSpawn"))
        self.animation_clone_idle = AnimationManager(assetMgr.getAnim("MoonC"))
        self.clone_asteroids = []
        self.clone_move_dir = -1
        self.clone_teleport_active = False
        self.clone_teleport_state = None
        self.clone_teleport_timer = 0
        self.clone_teleports_left = 0

        # Giant State
        self.giant_state = False
        self.giant_state_transition_animation = False
        self.animation_giant_transition = AnimationManager(assetMgr.getAnim("MoonP2TG"))
        self.animation_giant_idle = AnimationManager(assetMgr.getAnim("MoonG"))
        self.giant_triggered = False
        self.giant_timer = 0
        self.giant_duration = 480

        # Phase 2 Scarred
        self.phase2_scarred = False
        self.phase2_scarred_transition_animation = False
        self.animation_phase2_scarred_transition = AnimationManager(assetMgr.getAnim("MoonGTP2Scarred"))
        self.animation_phase2_scarred_idle = AnimationManager(assetMgr.getAnim("MoonP2Scarred"))

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
        self.selected_vanish = None
        self.selected_appear = None
        self.teleport_active = False
        self.teleport_state = None  # "vanish" / "appear" / "barrage" / "break" (what should I call this?)
        self.teleport_timer = 0
        self.teleports_left = 0
        self.teleportCount = 5
        self.teleportBreak = 0

        # Phase 1 Teleport
        self.animation_teleport_vanish = AnimationManager(assetMgr.getAnim("MoonTeleFastOut"), 24)
        self.animation_teleport_appear = AnimationManager(assetMgr.getAnim("MoonTeleFastIn"), 24)
        # Phase 2 Teleport
        self.animation_teleport2_vanish = AnimationManager(assetMgr.getAnim("MoonPha2TeleFastOut"), 24)
        self.animation_teleport2_appear = AnimationManager(assetMgr.getAnim("MoonPha2TeleFastIn"), 24)
        # Clone Teleport
        self.animation_clone_teleport_vanish = AnimationManager(assetMgr.getAnim("CMoonTeleOut"), 24)
        self.animation_clone_teleport_appear = AnimationManager(assetMgr.getAnim("CMoonTeleIn"), 24)
        # Phase 3 Teleport
        self.animation_teleport3_vanish = AnimationManager(assetMgr.getAnim("MoonScarTeleSlowOut"), 24)
        self.animation_teleport3_appear = AnimationManager(assetMgr.getAnim("MoonScarTeleSlowIn"), 24)
        # Swapping Teleport
        self.swap_active = False
        self.swap_state = None

    # HP Bar Drawings
        # def HPBar(self):

    def move(self):
        if not self.moving:
            return
        self.rect.x += self.move_dir * self.move_speed
        if self.rect.left <= self.move_left_bound:
            self.move_dir = 1
        elif self.rect.right >= self.move_right_bound:
            self.move_dir = -1

    def takeDamage(self, damage):
        if self.invincibility:
            return
        self.hp -= damage
        if self.phase == 1 and self.hp <= self.phase2_hp:
            self.phase = 2  # Triggers phase 2 transition animation
        elif self.phase == 2 and self.hp <= self.giant_hp:
            self.giant_state = True
            self.giant_triggered = True
            self.massRelease()
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, player_rect):
        if self.swap_active:
            self.updateSwap()
            return
        elif self.teleport_active:
            self.updateTeleport(player_rect)
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
                self.giant_timer -= 1
                self.updateGiantAttacks(player_rect)
                if self.giant_timer <= 0:
                    self.giant_state = False
                    self.phase = 3
                    self.invincibility = False
            else:
                self.clone_active = False
                self.animation_giant_transition.update(loop=False)
                lastFrameTrans = len(self.animation_giant_transition.frames) - 1
                if self.animation_giant_transition.index >= lastFrameTrans:
                    self.giant_state_transition_animation = True
                    self.giant_timer = self.giant_duration
        elif self.phase == 1:
            self.animation_phase1_idle.update()
        elif self.phase == 2:
            self.clone_active = True
            if self.phase2_transition_animation:
                self.animation_phase2_idle.update()
                self.animation_clone_idle.update()
            else:
                self.clone_rect = self.rect.copy()
                self.clone_rect.centerx = self.screen_w - self.rect.centerx
                self.animation_phase1_phase2_transition.update(loop=False)
                lastFrameTrans = len(self.animation_phase1_phase2_transition.frames) - 1
                self.animation_clone_spawn.update(loop=False)
                lastFrameClone = len(self.animation_clone_spawn.frames) - 1
                if self.animation_phase1_phase2_transition.index >= lastFrameTrans and self.animation_clone_spawn.index >= lastFrameClone:
                    self.phase2_transition_animation = True

    def draw(self, screen):
        frame = None
        frame2 = None
        if self.swap_active:
            if self.swap_state == "out":
                frame = self.animation_teleport2_vanish.get_current_frame()
                frame2 = self.animation_clone_teleport_vanish.get_current_frame()
            elif self.swap_state == "in":
                frame = self.animation_teleport2_appear.get_current_frame()
                frame2 = self.animation_clone_teleport_appear.get_current_frame()
        elif self.teleport_active:
            if self.teleport_state == "vanish":
                if self.phase == 1:
                    frame = self.animation_teleport_vanish.get_current_frame()
                elif self.phase == 2:
                    frame = self.animation_teleport2_vanish.get_current_frame()
                    frame2 = self.animation_clone_teleport_vanish.get_current_frame()
                elif self.phase == 3:
                    frame = self.animation_teleport3_vanish.get_current_frame()
            elif self.teleport_state == "appear":
                if self.phase == 1:
                    frame = self.animation_teleport_appear.get_current_frame()
                elif self.phase == 2:
                    frame = self.animation_teleport2_appear.get_current_frame()
                    frame2 = self.animation_clone_teleport_appear.get_current_frame()
                elif self.phase == 3:
                    frame = self.animation_teleport3_appear.get_current_frame()
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
        mass = Mass()
        mass.spawnLocation(player_rect, self.rect, screen_w, screen_h)
        self.active_masses.append(mass)

    def asteroidBarrage(self, player_rect):
        cx, cy = self.rect.center
        aim = math.atan2(player_rect.centery - cy, player_rect.centerx - cx)
        if self.clone_active:
            count = random.randint(3, 4)
        else:
            count = random.randint(5, 8)
        spread = math.radians(120)
        if self.phase == 1:
            asteroidType = "Neutral"
        elif self.phase == 2:
            asteroidType = "Fiery"
        else:
            asteroidType = "Scarred"
        for i in range(count):
            # t is made to even the spread of the asteroids
            t = i / (count - 1)
            angle = aim - spread / 2 + spread * t
            vx = math.cos(angle)
            vy = math.sin(angle)
            size = random.randint(26, 46)
            self.asteroids.append(Asteroid(cx, cy, vx, vy, size, asteroid_type=asteroidType))
        if self.clone_active:
            self.cloneBarrage(player_rect)

    def cloneBarrage(self, player_rect):
        cx, cy = self.clone_rect.center
        aim = math.atan2(player_rect.centery - cy, player_rect.centerx - cx)
        count = random.randint(3, 4)
        spread = math.radians(120)
        for i in range(count):
            t = i / (count - 1)
            angle = aim - spread / 2 + spread * t
            vx = math.cos(angle)
            vy = math.sin(angle)
            size = random.randint(26, 46)
            self.clone_asteroids.append(
                Asteroid(cx, cy, vx, vy, size, asteroid_type="Clone"))

    def cloneMass(self, player_rect):
        mass = Mass(True)
        mass.spawnLocation(player_rect, self.clone_rect, self.screen_w, self.screen_h)
        mass.generatedMass = random.randint(400, 700)  # significantly weaker
        mass.isCloneMass = True
        self.active_masses.append(mass)

    def moveClone(self):
        if not self.clone_active or self.teleport_active:
            return
        self.clone_rect.x += self.clone_move_dir * self.move_speed
        if self.clone_rect.left <= self.move_left_bound:
            self.clone_move_dir = 1
        elif self.clone_rect.right >= self.move_right_bound:
            self.clone_move_dir = -1

    def swapWithClone(self, player_rect):
        if not self.clone_active or self.swap_active or self.teleport_active:
            return
        self.swap_active = True
        self.swap_state = "out"
        self.moving = False
        self.invincibility = True
        self.player_rect = player_rect
        soundMgr.play_sfx("teleport out")
        self.animation_teleport2_vanish.index = 0
        self.animation_clone_teleport_vanish.index = 0

    def updateSwap(self):
        if not self.swap_active:
            return
        if self.swap_state == "out":
            self.animation_teleport2_vanish.update(loop=False)
            self.animation_clone_teleport_vanish.update(loop=False)
            real_done = self.animation_teleport2_vanish.index >= len(self.animation_teleport2_vanish.frames) - 1
            clone_done = self.animation_clone_teleport_vanish.index >= len(self.animation_clone_teleport_vanish.frames) - 1
            if real_done and clone_done:
                real_pos = self.rect.center
                clone_pos = self.clone_rect.center
                self.rect.center = clone_pos
                self.clone_rect.center = real_pos
                self.swap_state = "in"
                self.animation_teleport2_appear.index = 0
                self.animation_clone_teleport_appear.index = 0
                soundMgr.play_sfx("teleport in")

        elif self.swap_state == "in":
            self.animation_teleport2_appear.update(loop=False)
            self.animation_clone_teleport_appear.update(loop=False)
            real_done = self.animation_teleport2_appear.index >= len(self.animation_teleport2_appear.frames) - 1
            clone_done = self.animation_clone_teleport_appear.index >= len(self.animation_clone_teleport_appear.frames) - 1
            if real_done and clone_done:
                self.asteroidBarrage(self.player_rect)
                self.endSwap()

    def endSwap(self):
        self.swap_active = False
        self.swap_state = None
        self.moving = True
        self.invincibility = False

    def massRelease(self):
        self.giant_state = True
        self.invincibility = True

    def teleportAttack(self, player_rect, screen_w, screen_h):
        if self.teleport_active:
            return
        self.teleport_active = True
        self.teleports_left = self.teleportCount
        self.moving = False  # Stop movement during teleportation
        self.invincibility = True
        self.player_rect = player_rect
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.beginTeleport()

    def beginTeleport(self):
        self.teleport_state = "vanish"
        soundMgr.play_sfx("teleport out")
        if self.phase == 1:
            self.teleport_timer = len(self.animation_teleport_vanish.frames)
            self.animation_teleport_vanish.index = 0
        elif self.phase == 2:
            self.teleport_timer = len(self.animation_teleport2_vanish.frames)
            self.animation_teleport2_vanish.index = 0
            self.teleport_timer = len(self.animation_teleport2_vanish.frames)
            self.animation_clone_teleport_vanish.index = 0
        else:
            self.teleport_timer = len(self.animation_teleport2_vanish.frames)
            self.animation_teleport2_vanish.index = 0

    def updateTeleport(self, player_rect):
        if not self.teleport_active:
            return

        if self.phase == 1:
            self.selected_vanish = self.animation_teleport_vanish
            self.selected_appear = self.animation_teleport_appear
        elif self.phase == 2:
            self.selected_vanish = self.animation_teleport2_vanish
            self.selected_appear = self.animation_teleport2_appear
        else:
            self.selected_vanish = self.animation_teleport3_vanish
            self.selected_appear = self.animation_teleport3_appear

        if self.teleport_state == "vanish":
            self.selected_vanish.update(loop=False)
            if self.clone_active:
                self.animation_clone_teleport_vanish.update(loop=False)
            if self.selected_vanish.index >= len(self.selected_vanish.frames) - 1:
                new_x = random.randint(self.move_left_bound, self.move_right_bound)
                new_y = random.randint(120, int(self.screen_h * 0.6))
                self.rect.center = (new_x, new_y)
                min_dist = 300
                if math.hypot(new_x - player_rect.centerx, new_y - player_rect.centery) < min_dist:
                    for i in range(100):
                        new_x = random.randint(self.move_left_bound, self.move_right_bound)
                        new_y = random.randint(120, int(self.screen_h * 0.6))
                        distanceToPlayer = math.hypot(new_x - player_rect.centerx, new_y - player_rect.centery)
                        if distanceToPlayer >= min_dist:
                            self.rect.center = (new_x, new_y)
                if self.clone_active:
                    self.cloneTeleport(self.rect.center, player_rect)
                    self.animation_clone_teleport_appear.index = 0
                soundMgr.play_sfx("teleport in")
                self.teleport_state = "appear"
                self.selected_appear.index = 0

        elif self.teleport_state == "appear":
            self.selected_appear.update(loop=False)
            if self.clone_active:
                self.animation_clone_teleport_appear.update(loop=False)
            if self.selected_appear.index >= len(self.selected_appear.frames) - 1:
                soundMgr.play_sfx("asteroid")
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

    def cloneTeleport(self, real_pos, player_rect):
        minDistMoon = 500
        minDistPlayer = 250
        rx, ry = real_pos
        for i in range(100):
            cx = random.randint(self.move_left_bound, self.move_right_bound)
            cy = random.randint(120, int(self.screen_h * 0.6))
            far_from_real = math.hypot(cx - rx, cy - ry) >= minDistMoon
            far_from_player = math.hypot(cx - player_rect.centerx, cy - player_rect.centery) >= minDistPlayer
            if far_from_real and far_from_player:
                self.clone_rect.center = (cx, cy)
                return
        self.clone_rect.center = (self.screen_w - rx, ry)

    def updateGiantAttacks(self, player_rect):
        if not hasattr(self, 'giant_attack_timer'):
            self.giant_attack_timer = 0
        self.giant_attack_timer -= 1
        if self.giant_attack_timer <= 0:
            self.giantBarrage(player_rect)
            self.giant_attack_timer = 40

    def giantBarrage(self, player_rect):
        cx, cy = self.rect.center
        aim = math.atan2(player_rect.centery - cy, player_rect.centerx - cx)
        count = 10
        spread = math.radians(160)
        for i in range(count):
            t = i / (count - 1)
            angle = aim - spread / 2 + spread * t
            vx, vy = math.cos(angle), math.sin(angle)
            size = random.randint(30, 50)
            self.asteroids.append(Asteroid(cx, cy, vx, vy, size, asteroid_type="Eclipse"))

    def chooseMove(self, player_rect):
        if self.teleport_active or self.giant_state:
            return
        if not hasattr(self, 'move_cooldown'):
            self.move_cooldown = 0
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dist = math.hypot(player_rect.centerx - self.rect.centerx,
                          player_rect.centery - self.rect.centery)

        # Decision Tree
        if self.phase == 1:
            if dist > self.screen_h * 0.5:
                self.asteroidBarrage(player_rect)
            else:
                choice = random.choice(["barrage", "teleport", "gravity"])
                if choice == "barrage":
                    self.asteroidBarrage(player_rect)
                elif choice == "teleport":
                    self.teleportAttack(player_rect, self.screen_w, self.screen_h)
                else:
                    self.gravityPull(player_rect, self.screen_w, self.screen_h)
            self.move_cooldown = random.randint(60, 120)

        elif self.phase == 2:
            if dist < self.radius + 150:
                self.swapWithClone(player_rect)
            else:
                choice = random.choice(["barrage", "teleport", "gravity", "swap"])
                if choice == "barrage":
                    self.asteroidBarrage(player_rect)
                elif choice == "teleport":
                    self.teleportAttack(player_rect, self.screen_w, self.screen_h)
                elif choice == "gravity":
                    self.gravityPull(player_rect, self.screen_w, self.screen_h)
                    self.cloneMass(player_rect)
                else:
                    self.swapWithClone(player_rect)
            self.move_cooldown = random.randint(45, 90)

        elif self.phase == 3:
            choice = random.choice(["barrage", "teleport", "gravity", "beam"])
            if choice == "barrage":
                self.asteroidBarrage(player_rect)
            elif choice == "teleport":
                self.teleportAttack(player_rect, self.screen_w, self.screen_h)
            elif choice == "gravity":
                self.gravityPull(player_rect, self.screen_w, self.screen_h)
            self.move_cooldown = random.randint(30, 70)

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
            size = 30
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
                soundMgr.play_sfx("asteroid")
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

        self.rotated_image = self.image
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        if self.fixed_speed is None:
            self.speed += 0.2
            if self.speed > 15:
                self.speed = 15
        self.fx += self.vx * self.speed
        self.fy += self.vy * self.speed
        self.rect.center = (int(self.fx), int(self.fy))
        self.angle += (self.speed * 2) % 360

        # Perform rotation here during the physics update
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        # Update self.rect to match the expanded rotated boundaries, keeping center locked
        self.rect = self.rotated_image.get_rect(center=(int(self.fx), int(self.fy)))
        # Generate a pixel-perfect mask from this frame's rotated image
        self.mask = pygame.mask.from_surface(self.rotated_image)

    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect)

        for point in self.mask.outline():
            screen.set_at((self.rect.x + point[0], self.rect.y + point[1]), (255, 255, 0))

    def removeAsteroid(self, w, h):
        return(self.rect.right < -200 or self.rect.left > w + 200 or
               self.rect.bottom < -200 or self.rect.top > h + 200)

class Mass:
    G = 6.674
    def __init__(self, isClone=False):
        self.life = 100
        self.radius = 30
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.generatedMass = random.randint(1000, 1500)
        self.animation = AnimationManager(assetMgr.getAnim("Mass"))
        self.animation_spawn = AnimationManager(assetMgr.getAnim("MassSpawn"))
        self.animation_despawn = AnimationManager(assetMgr.getAnim("MassDespawn"))
        self.isCloneMass = isClone
        self.animation_spawn_loaded = False
        self.animation_despawn_loaded = False
        self.isDead = False
        if self.isCloneMass:
            self.animation = AnimationManager(assetMgr.getAnim("MassX"))
            self.animation_spawn = AnimationManager(assetMgr.getAnim("CloneMassSpawn"))
            self.animation_despawn = AnimationManager(assetMgr.getAnim("CloneMassDespawn"))
        else:
            self.animation = AnimationManager(assetMgr.getAnim("Mass"))
            self.animation_spawn = AnimationManager(assetMgr.getAnim("MassSpawn"))
            self.animation_despawn = AnimationManager(assetMgr.getAnim("MassDespawn"))

    def update(self):
        if self.isDead:
            return
        elif self.life <= 0:
            self.animation_despawn.update(loop=False)
            lastFrameTrans = len(self.animation_despawn.frames) - 1
            if self.animation_despawn.index >= lastFrameTrans:
                self.animation_despawn_loaded = True
                self.isDead = True
                soundMgr.stop_sfx("mass active")
        elif self.life > 0 and not self.isDead:
            if self.animation_spawn_loaded:
                self.animation.update()
                self.life -= 1
            else:
                self.animation_spawn.update(loop=False)
                lastFrameTrans = len(self.animation_spawn.frames) - 1
                if self.animation_spawn.index >= lastFrameTrans:
                    self.animation_spawn_loaded = True
                    soundMgr.loop_sfx("mass active", 0.5)

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
        if (not self.isCloneMass):
            force = max(1.5, force)
        # Ensures force is not overly strong when near
        force = min(6.0, force)
        nx, ny = dx / dist, dy / dist
        pull_x = int(nx * force)
        pull_y = int(ny * force)
        player_rect.x += pull_x
        player_rect.y += pull_y
        return (pull_x, pull_y)