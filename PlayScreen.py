import pygame
import math
import json
import os

class PlayScreen:
    STATE_FADEIN  = "fadein"
    STATE_ACTIVE  = "active"
    STATE_FADEOUT = "fadeout"

    def __init__(self, screen_w, screen_h, score_manager):
        self.sw = screen_w
        self.sh = screen_h
        self.state = self.STATE_FADEIN
        self.timer = 0

        # Fonts
        self.font_title  = pygame.font.Font("PressStart2P-Regular.ttf", 14)
        self.font_medium = pygame.font.Font("PressStart2P-Regular.ttf", 11)
        self.font_small  = pygame.font.Font("PressStart2P-Regular.ttf", 9)

        # Fade
        self.fade_alpha   = 255
        self.fade_speed   = 6
        self.fade_surface = pygame.Surface((screen_w, screen_h))
        self.fade_surface.fill((0, 0, 0))

        # Text input
        self.player_name     = ""
        self.max_chars       = 8
        self.cursor_timer    = 0
        self.cursor_visible  = True
        self.input_flash     = 0   # red flash when empty on confirm

        # Difficulty
        self.difficulty       = None
        self.diff_flash       = 0  # red flash when not selected on confirm

        # Confirm flash
        self.confirm_flash    = 0

        # Action — main.py reads this
        self.action = None

        # Save file
        # Removed this because score manager handles this

        self.score_manager = score_manager

        # ── Layout ──────────────────────────────────────────
        cx = self.sw // 2  # center x

        # Input box
        self.input_rect = pygame.Rect(cx - 160, 160, 320, 48)

        # Colors
        COLOR_BTN        = (30,  0,  80)
        COLOR_BTN_HOVER  = (80,  0, 180)
        COLOR_BTN_SEL    = (0,  120, 220)   # highlighted difficulty
        COLOR_QUIT       = (60,  0,   0)
        COLOR_QUIT_HOVER = (180, 0,   0)
        COLOR_CONFIRM        = (0,  80,  0)
        COLOR_CONFIRM_HOVER  = (0, 160,  0)

        self.color_btn_sel = COLOR_BTN_SEL

        btn_w, btn_h = 220, 44
        diff_w       = 160

        # USE LAST NAME button
        self.btn_last = _Button("USE LAST NAME", self.font_small,
                                cx - 110, 224, 220, 36,
                                COLOR_BTN, COLOR_BTN_HOVER)

        # Difficulty buttons  (y = 360)
        diff_y   = 360
        diff_gap = 180
        self.btn_easy   = _Button("EASY",   self.font_medium,
                                  cx - diff_gap - diff_w//2, diff_y,
                                  diff_w, btn_h, COLOR_BTN, COLOR_BTN_HOVER)
        self.btn_medium = _Button("MEDIUM", self.font_medium,
                                  cx - diff_w//2,            diff_y,
                                  diff_w, btn_h, COLOR_BTN, COLOR_BTN_HOVER)
        self.btn_hard   = _Button("HARD",   self.font_medium,
                                  cx + diff_gap - diff_w//2, diff_y,
                                  diff_w, btn_h, COLOR_BTN, COLOR_BTN_HOVER)

        self.diff_buttons = [
            (self.btn_easy,   "Easy"),
            (self.btn_medium, "Medium"),
            (self.btn_hard,   "Hard"),
        ]

        # Confirm / Back
        self.btn_confirm = _Button("CONFIRM", self.font_medium,
                                   cx - btn_w//2, 460, btn_w, btn_h,
                                   COLOR_CONFIRM, COLOR_CONFIRM_HOVER)
        self.btn_back    = _Button("BACK",    self.font_medium,
                                   cx - btn_w//2, 524, btn_w, btn_h,
                                   COLOR_QUIT, COLOR_QUIT_HOVER)

        self.all_buttons = [
            self.btn_last,
            self.btn_easy, self.btn_medium, self.btn_hard,
            self.btn_confirm, self.btn_back,
        ]

    # Save helpers
    #have removed because the logic is duplicat, so score manager should handle saving
    def load_last_name(self):
        name = self.score_manager.get_last_name()
        if name:
            self.player_name = name[:self.max_chars]

    # ── Update ──────────────────────────────────────────────
    def update(self, events):
        self.timer       += 1
        self.cursor_timer += 1
        self.action       = None

        # Blink cursor every 30 frames
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer   = 0

        # Tick flash timers down
        if self.input_flash   > 0: self.input_flash   -= 1
        if self.diff_flash    > 0: self.diff_flash    -= 1
        if self.confirm_flash > 0: self.confirm_flash -= 1

        # ── Fade in ──
        if self.state == self.STATE_FADEIN:
            self.fade_alpha -= self.fade_speed * 2
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.state = self.STATE_ACTIVE
            return

        # ── Fade out ──
        if self.state == self.STATE_FADEOUT:
            self.fade_alpha += self.fade_speed * 2
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                # Signal main.py with whatever action triggered the fadeout
                self.action = self._pending_action
            return

        # ── Active ──
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.all_buttons:
            btn.check_hover(mouse_pos)

        for event in events:
            # ── Keyboard ──
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._try_confirm()

                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]

                else:
                    char = event.unicode
                    if char.isalnum() or char in ("-", "_"):
                        if len(self.player_name) < self.max_chars:
                            self.player_name += char.upper()

            # ── Mouse click ──
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # USE LAST NAME
                if self.btn_last.is_clicked(mouse_pos):
                    self.load_last_name()

                # Difficulty toggle
                for btn, label in self.diff_buttons:
                    if btn.is_clicked(mouse_pos):
                        self.difficulty = label

                # Confirm
                if self.btn_confirm.is_clicked(mouse_pos):
                    self._try_confirm()

                # Back
                if self.btn_back.is_clicked(mouse_pos):
                    self._start_fadeout("BACK")

    def _try_confirm(self):
        name_ok = len(self.player_name.strip()) > 0
        diff_ok = self.difficulty is not None
        if name_ok and diff_ok:
            self._start_fadeout("START")
        else:
            if not name_ok:  self.input_flash   = 30
            if not diff_ok:  self.diff_flash     = 30
            self.confirm_flash = 30

    def _start_fadeout(self, action):
        self._pending_action = action
        self.state           = self.STATE_FADEOUT
        self.fade_alpha      = 0

    # ── Draw ────────────────────────────────────────────────
    def draw(self, screen):
        cx = self.sw // 2

        # ── "ENTER YOUR CALLSIGN" label ──
        label = self.font_title.render("ENTER YOUR CALLSIGN", True, (200, 200, 255))
        screen.blit(label, label.get_rect(center=(cx, 110)))

        # ── Input box ──
        input_color = (220, 50, 50) if self.input_flash > 0 else (180, 180, 255)
        pygame.draw.rect(screen, (10, 0, 30),    self.input_rect, border_radius=6)
        pygame.draw.rect(screen, input_color,    self.input_rect, 2, border_radius=6)

        # Typed text + blinking cursor
        display_text = self.player_name
        if self.cursor_visible and self.state == self.STATE_ACTIVE:
            display_text += "|"
        name_surf = self.font_medium.render(display_text, True, (255, 255, 255))
        name_rect = name_surf.get_rect(center=self.input_rect.center)
        screen.blit(name_surf, name_rect)

        # ── USE LAST NAME ──
        self.btn_last.draw(screen)

        # ── "SELECT DIFFICULTY" label ──
        diff_label_color = (220, 50, 50) if self.diff_flash > 0 else (200, 200, 255)
        diff_label = self.font_title.render("SELECT DIFFICULTY", True, diff_label_color)
        screen.blit(diff_label, diff_label.get_rect(center=(cx, 310)))

        # ── Difficulty buttons ──
        for btn, label in self.diff_buttons:
            is_selected = self.difficulty == label
            btn.draw(screen, selected=is_selected,
                     selected_color=self.color_btn_sel)

        # ── CONFIRM ──
        confirm_color_override = (180, 0, 0) if self.confirm_flash > 0 else None
        self.btn_confirm.draw(screen, color_override=confirm_color_override)

        # ── BACK ──
        self.btn_back.draw(screen)

        # ── Fade overlay ──
        if self.fade_alpha > 0:
            self.fade_surface.set_alpha(self.fade_alpha)
            screen.blit(self.fade_surface, (0, 0))


# ── Private Button class (internal to this module) ──────────
class _Button:
    def __init__(self, text, font, x, y, width, height, color, hover_color):
        self.text        = text
        self.font        = font
        self.x           = x
        self.y           = y
        self.width       = width
        self.height      = height
        self.color       = color
        self.hover_color = hover_color
        self.hovered     = False

    def draw(self, screen, selected=False, selected_color=None, color_override=None):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if color_override:
            fill = color_override
        elif selected and selected_color:
            fill = selected_color
        elif self.hovered:
            fill = self.hover_color
        else:
            fill = self.color

        pygame.draw.rect(screen, fill,           rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def check_hover(self, mouse_pos):
        self.hovered = pygame.Rect(
            self.x, self.y, self.width, self.height
        ).collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return pygame.Rect(
            self.x, self.y, self.width, self.height
        ).collidepoint(mouse_pos)