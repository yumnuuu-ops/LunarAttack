import pygame


class HUD:
    COMBO_TIMEOUT = 3.0
    MAX_COMBO = 8

    DIFF_MULTIPLIER = {
        "Easy": 1.0,
        "Medium": 1.5,
        "Hard": 2.0,
        "Eclipse": 4.0,
    }

    DIFF_HEARTS = {
        "Easy": 15,
        "Medium": 10,
        "Hard": 5,
        "Eclipse": 1,
    }

    MAX_SLOTS = 5
    CHARGES_PER_SLOT = 3
    FLASH_DURATION = 20  # frames

    def __init__(self, screen_w, screen_h, player_name, difficulty, player):
        self.sw = screen_w
        self.sh = screen_h
        self.player_name = player_name
        self.difficulty = difficulty
        self.multiplier = self.DIFF_MULTIPLIER.get(difficulty, 1.0)

        self.font_large = pygame.font.Font("PressStart2P-Regular.ttf", 11)
        self.font_medium = pygame.font.Font("PressStart2P-Regular.ttf", 8)
        self.font_small = pygame.font.Font("PressStart2P-Regular.ttf", 7)

        # score
        self.score = 0
        self.display_score = 0

        # combo
        self.combo = 1
        self.combo_timer = 0.0
        self.combo_active = False
        self.combo_flash = 0

    
        

        # heart images
        self.heart_imgs = {
            3: pygame.transform.scale(pygame.image.load("imgs/HUD/heart3.png").convert_alpha(), (28, 25)),
            2: pygame.transform.scale(pygame.image.load("imgs/HUD/heart2.png").convert_alpha(), (28, 25)),
            1: pygame.transform.scale(pygame.image.load("imgs/HUD/heart1.png").convert_alpha(), (28, 25)),
            0: pygame.transform.scale(pygame.image.load("imgs/HUD/heart_dead.png").convert_alpha(), (28, 25)),
        }
        player.hp = self.DIFF_HEARTS.get(difficulty, 3)

        # white flash overlay
        self.flash_overlay = pygame.Surface((28, 25), pygame.SRCALPHA)
        self.flash_overlay.fill((255, 255, 255, 180))

        # total charges and slot system
        total_charges = self.DIFF_HEARTS.get(difficulty, 5)
        self.slots = []  # list of 5 charge values (0-3)
        self.flash_slots = [0] * self.MAX_SLOTS  # flash timer per slot

        remaining = total_charges
        for i in range(self.MAX_SLOTS):
            charge = min(self.CHARGES_PER_SLOT, remaining)
            self.slots.append(charge)
            remaining -= charge
            if remaining < 0:
                remaining = 0

        # wave
        self.current_wave = 1
        self.current_stage = 1
        self.wave_time = 0.0

        # weapon
        self.weapon_name = "AUTO CANNON"

        # no damage bonus
        self.took_damage_this_wave = False

        self.on_game_over = lambda: None

    def set_weapon(self, weapon_key):
        name_map = {
            "AutoCannon": "AUTO CANNON",
            "Rockets": "ROCKETS",
            "Zapper": "ZAPPER",
            "BigGun": "BIG GUN",
        }
        self.weapon_name = name_map.get(weapon_key, weapon_key)

    def update(self, dt):
        # combo timer
        if self.combo_active:
            self.combo_timer += dt
            if self.combo_timer >= self.COMBO_TIMEOUT:
                self.reset_combo()

        # wave timer
        self.wave_time += dt

        # display score tick
        if self.display_score < self.score:
            diff = self.score - self.display_score
            self.display_score += max(1, diff // 8)
            if self.display_score > self.score:
                self.display_score = self.score

        # combo flash
        if self.combo_flash > 0:
            self.combo_flash -= 1

        # flash timers per slot
        for i in range(self.MAX_SLOTS):
            if self.flash_slots[i] > 0:
                self.flash_slots[i] -= 1

    def register_kill(self, base_points):
        self.combo_timer = 0.0
        self.combo_active = True
        points = int(base_points * self.combo * self.multiplier)
        self.score += points
        if self.combo < self.MAX_COMBO:
            self.combo += 1
            self.combo_flash = 30
        return points

    def reset_combo(self):
        self.combo = 1
        self.combo_timer = 0.0
        self.combo_active = False
        self.combo_flash = 0

    def take_damage(self):
        # find rightmost slot with charges
        for i in range(self.MAX_SLOTS - 1, -1, -1):
            if self.slots[i] > 0:
                self.slots[i] -= 1
                self.flash_slots[i] = self.FLASH_DURATION
                self.took_damage_this_wave = True
                break

        # check game over
        if all(c == 0 for c in self.slots):
            self.on_game_over()

    def next_wave(self):
        bonus = 500
        if not self.took_damage_this_wave:
            bonus += 1000
        self.score += int(bonus * self.multiplier)
        self.current_wave += 1
        self.current_stage += 1
        self.wave_time = 0.0
        self.took_damage_this_wave = False
        self.reset_combo()

    def add_boss_hit(self):
        self.score += int(150 * self.multiplier)

    def add_boss_kill(self):
        self.score += int(5000 * self.multiplier)

    def _format_time(self, seconds):
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02}:{s:02}"

    def _draw_panel(self, screen, x, y, w, h):
        panel = pygame.Surface((w, h))
        panel.set_alpha(140)
        panel.fill((0, 0, 0))
        screen.blit(panel, (x, y))
        pygame.draw.rect(screen, (80, 80, 120), (x, y, w, h), 1)

    def _draw_hearts(self, screen, x, y):
        spacing = 34
        for i in range(self.MAX_SLOTS):
            hx = x + i * spacing
            charge = self.slots[i]
            img = self.heart_imgs[charge]
            screen.blit(img, (hx, y))

            # white flash overlay when charge just dropped
            if self.flash_slots[i] > 0:
                flash_surf = self.flash_overlay.copy()
                alpha = int((self.flash_slots[i] / self.FLASH_DURATION) * 180)
                flash_surf.set_alpha(alpha)
                screen.blit(flash_surf, (hx, y))

    def draw(self, screen):
        pad = 16

        # top left panel
        self._draw_panel(screen, 0, 0, 200, 90)

        score_surf = self.font_medium.render(f"SCORE  {self.display_score:07}", True, (255, 255, 255))
        screen.blit(score_surf, (pad, pad))

        if self.combo > 1 or self.combo_flash > 0:
            flash_color = (255, 220, 50) if self.combo_flash > 0 else (180, 180, 100)
            combo_surf = self.font_medium.render(f"COMBO  x{self.combo}", True, flash_color)
            screen.blit(combo_surf, (pad, pad + 24))
        else:
            combo_surf = self.font_medium.render("COMBO  x1", True, (80, 80, 80))
            screen.blit(combo_surf, (pad, pad + 24))

        time_surf = self.font_medium.render(f"TIME   {self._format_time(self.wave_time)}", True, (180, 180, 255))
        screen.blit(time_surf, (pad, pad + 48))

        # top right panel
        panel_w = 200
        panel_x = self.sw - panel_w
        self._draw_panel(screen, panel_x, 0, panel_w, 100)

        name_surf = self.font_medium.render(f"CADET  {self.player_name[:8]}", True, (50, 220, 100))
        screen.blit(name_surf, (panel_x + pad, pad))

        self._draw_hearts(screen, panel_x + pad, pad + 22)

        stage_surf = self.font_medium.render(f"STAGE  {self.current_stage}", True, (180, 180, 255))
        screen.blit(stage_surf, (panel_x + pad, pad + 62))

        diff_colors = {
            "Easy": (50, 220, 80),
            "Medium": (220, 180, 50),
            "Hard": (220, 50, 50),
            "Eclipse": (160, 0, 220),
        }
        diff_color = diff_colors.get(self.difficulty, (255, 255, 255))
        diff_surf = self.font_small.render(self.difficulty.upper(), True, diff_color)
        screen.blit(diff_surf, (panel_x + pad + stage_surf.get_width() + 60, pad + 63))

        # weapon bottom center
        weapon_colors = {
            "AUTO CANNON": (255, 140, 0),
            "ROCKETS": (220, 50, 50),
            "ZAPPER": (50, 150, 255),
            "BIG GUN": (50, 220, 100),
        }
        weapon_color = weapon_colors.get(self.weapon_name, (255, 255, 255))

        weapon_label = self.font_small.render("WEAPON", True, weapon_color)
        weapon_name = self.font_medium.render(self.weapon_name, True, weapon_color)

        label_rect = weapon_label.get_rect(centerx=self.sw // 2, bottom=self.sh - 28)
        name_rect = weapon_name.get_rect(centerx=self.sw // 2, bottom=self.sh - 10)

        panel_rect = pygame.Rect(name_rect.left - 16, label_rect.top - 6,
                                 name_rect.width + 32, self.sh - label_rect.top + 6)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 80, 120), panel_rect, 1, border_radius=4)

        screen.blit(weapon_label, label_rect)
        screen.blit(weapon_name, name_rect)