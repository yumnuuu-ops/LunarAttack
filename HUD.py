import pygame

class HUD:
    COMBO_TIMEOUT = 3.0  # seconds before combo resets
    MAX_COMBO     = 10

    DIFF_MULTIPLIER = {
        "Easy"  : 1.0,
        "Medium": 1.5,
        "Hard"  : 2.0,
    }

    def __init__(self, screen_w, screen_h, player_name, difficulty):
        self.sw          = screen_w
        self.sh          = screen_h
        self.player_name = player_name
        self.difficulty  = difficulty
        self.multiplier  = self.DIFF_MULTIPLIER.get(difficulty, 1.0)

        self.font_large  = pygame.font.Font("PressStart2P-Regular.ttf", 10)
        self.font_medium = pygame.font.Font("PressStart2P-Regular.ttf", 7)
        self.font_small  = pygame.font.Font("PressStart2P-Regular.ttf", 6)

        # score
        self.score        = 0
        self.display_score = 0  # ticks up toward real score for visual effect

        # combo
        self.combo         = 1
        self.combo_timer   = 0.0
        self.combo_active  = False
        self.combo_flash   = 0   # frames to flash combo text

        # health
        self.max_hp  = 100
        self.hp      = 100

        # wave
        self.current_wave = 1
        self.current_stage = 1

        # time survived this wave
        self.wave_time = 0.0

        # weapon name
        self.weapon_name = "ZAPPER"

        # no damage bonus tracking
        self.took_damage_this_wave = False

    # called every frame
    def update(self, dt):
        # tick combo timer
        if self.combo_active:
            self.combo_timer += dt
            if self.combo_timer >= self.COMBO_TIMEOUT:
                self.reset_combo()

        # tick wave timer
        self.wave_time += dt

        # tick display score toward real score
        if self.display_score < self.score:
            diff = self.score - self.display_score
            self.display_score += max(1, diff // 8)
            if self.display_score > self.score:
                self.display_score = self.score

        # tick combo flash
        if self.combo_flash > 0:
            self.combo_flash -= 1

    def register_kill(self, base_points):
        # reset combo timer on each kill
        self.combo_timer  = 0.0
        self.combo_active = True

        # calculate points with combo and difficulty multiplier
        points = int(base_points * self.combo * self.multiplier)
        self.score += points

        # increase combo up to max
        if self.combo < self.MAX_COMBO:
            self.combo      += 1
            self.combo_flash = 30  # flash for 30 frames

        return points  # return so main can display floating text later

    def reset_combo(self):
        self.combo        = 1
        self.combo_timer  = 0.0
        self.combo_active = False
        self.combo_flash  = 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.took_damage_this_wave = True

    def next_wave(self):
        # wave clear bonus
        bonus = 500
        if not self.took_damage_this_wave:
            bonus += 1000  # no damage bonus

        self.score += int(bonus * self.multiplier)
        self.current_wave          += 1
        self.current_stage         += 1
        self.wave_time              = 0.0
        self.took_damage_this_wave  = False
        self.reset_combo()

    def add_boss_hit(self):
        points = int(150 * self.multiplier)
        self.score += points

    def add_boss_kill(self):
        points = int(5000 * self.multiplier)
        self.score += points

    def set_weapon(self, name):
        self.weapon_name = name

    def _hp_color(self):
        ratio = self.hp / self.max_hp
        if ratio > 0.6:
            return (50, 220, 80)   # green
        elif ratio > 0.3:
            return (220, 180, 50)  # yellow
        else:
            return (220, 50, 50)   # red

    def _draw_bar(self, screen, x, y, w, h, value, max_value, color):
        # background
        pygame.draw.rect(screen, (30, 30, 30), (x, y, w, h), border_radius=3)
        # fill
        fill_w = int((value / max_value) * w)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (x, y, fill_w, h), border_radius=3)
        # border
        pygame.draw.rect(screen, (180, 180, 180), (x, y, w, h), 1, border_radius=3)

    def _format_time(self, seconds):
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02}:{s:02}"

    def _draw_panel(self, screen, x, y, w, h):
        panel = pygame.Surface((w, h))
        panel.set_alpha(160)
        panel.fill((0, 0, 0))
        screen.blit(panel, (x, y))
        pygame.draw.rect(screen, (80, 80, 120), (x, y, w, h), 1)

    def draw(self, screen):
        pad = 16

        # dark panel top left
        self._draw_panel(screen, 0, 0, 220, 100)

        # score
        score_surf = self.font_medium.render(f"SCORE  {self.display_score:07}", True, (255, 255, 255))
        screen.blit(score_surf, (pad, pad))

        # combo
        if self.combo > 1 or self.combo_flash > 0:
            flash_color = (255, 220, 50) if self.combo_flash > 0 else (180, 180, 100)
            combo_surf  = self.font_medium.render(f"COMBO  x{self.combo}", True, flash_color)
            screen.blit(combo_surf, (pad, pad + 24))
        else:
            combo_surf = self.font_medium.render("COMBO  x1", True, (80, 80, 80))
            screen.blit(combo_surf, (pad, pad + 24))

        # time
        time_surf = self.font_medium.render(f"TIME   {self._format_time(self.wave_time)}", True, (180, 180, 255))
        screen.blit(time_surf, (pad, pad + 48))

        # dark panel top right
        panel_w = 240
        panel_x = self.sw - panel_w
        self._draw_panel(screen, panel_x, 0, panel_w, 110)

        # player name
        name_surf = self.font_medium.render(f"CADET  {self.player_name[:8]}", True, (50, 220, 100))
        screen.blit(name_surf, (panel_x + pad, pad))

        # hp label
        hp_label = self.font_small.render(f"HP  {self.hp}/{self.max_hp}", True, self._hp_color())
        screen.blit(hp_label, (panel_x + pad, pad + 26))

        # hp bar
        self._draw_bar(screen, panel_x + pad, pad + 40, panel_w - pad * 2, 12,
                       self.hp, self.max_hp, self._hp_color())

        # stage
        stage_surf = self.font_medium.render(f"STAGE  {self.current_stage}", True, (180, 180, 255))
        screen.blit(stage_surf, (panel_x + pad, pad + 62))

        # difficulty tag
        diff_colors = {
            "Easy"  : (50, 220, 80),
            "Medium": (220, 180, 50),
            "Hard"  : (220, 50, 50),
        }
        diff_color = diff_colors.get(self.difficulty, (255, 255, 255))
        diff_surf  = self.font_small.render(self.difficulty.upper(), True, diff_color)
        screen.blit(diff_surf, (panel_x + pad, pad + 88))

        # weapon bottom center
        weapon_label = self.font_small.render("WEAPON", True, (120, 120, 180))
        weapon_name  = self.font_medium.render(self.weapon_name, True, (255, 255, 255))

        label_rect  = weapon_label.get_rect(centerx=self.sw // 2, bottom=self.sh - 28)
        name_rect   = weapon_name.get_rect(centerx=self.sw // 2,  bottom=self.sh - 10)

        # weapon panel background
        panel_rect = pygame.Rect(name_rect.left - 16, label_rect.top - 6,
                                 name_rect.width + 32, self.sh - label_rect.top + 6)
        pygame.draw.rect(screen, (0, 0, 0), panel_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 80, 120), panel_rect, 1, border_radius=4)

        screen.blit(weapon_label, label_rect)
        screen.blit(weapon_name,  name_rect)