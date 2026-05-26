import pygame
import math


class Button:
    def __init__(self, text, font, x, y, width, height, color, hover_color):
        self.text = text
        self.font = font
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.hovered = False
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, offset_y=0):
        draw_rect = pygame.Rect(self.x, self.y + offset_y, self.width, self.height)
        color = self.hover_color if self.hovered else self.color

        pygame.draw.rect(screen, color, draw_rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), draw_rect, 2, border_radius=6)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=draw_rect.center)
        screen.blit(text_surf, text_rect)

    # mouse hover
    def check_hover(self, mouse_pos, offset_y=0):
        draw_rect = pygame.Rect(self.x, self.y + offset_y, self.width, self.height)
        self.hovered = draw_rect.collidepoint(mouse_pos)

    # mouse press
    def is_clicked(self, mouse_pos, offset_y=0):
        draw_rect = pygame.Rect(self.x, self.y + offset_y, self.width, self.height)
        return draw_rect.collidepoint(mouse_pos)


# these are the states menu can be in!!
class MainMenu:
    STATE_TITLE = "title"
    STATE_SLIDING = "sliding"
    STATE_MENU = "menu"
    STATE_SLIDEOUT = "slideout"

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.state = self.STATE_TITLE
        self.timer = 0

        self.font_large = pygame.font.Font("PressStart2P-Regular.ttf", 14)
        self.font_small = pygame.font.Font("PressStart2P-Regular.ttf", 10)

        self.lunar = pygame.image.load("imgs/MainMenu/LUNAR.png").convert_alpha()
        self.attack = pygame.image.load("imgs/MainMenu/ATTACK.png").convert_alpha()
        self.planet = pygame.transform.scale(
            pygame.image.load("imgs/MainMenu/bigPlanet.png").convert_alpha(), (220, 220)
        )
        self.asteroid = pygame.transform.scale(
            pygame.image.load("imgs/MainMenu/asteroid1.png").convert_alpha(), (180, 180)
        )

        self.logo_y = self.sh // 2 - 360
        self.logo_y_target_title = self.sh // 2 - 360
        self.logo_y_target_menu  = -150

        self.buttons_y = self.sh
        self.buttons_y_target_hidden = self.sh
        self.buttons_y_target_shown  = 0

        self.flash_timer = 0
        self.flash_visible = True

        # main.py reads this to know what button was pressed
        self.action = None

        btn_w, btn_h = 260, 45
        btn_x = self.sw // 2 - btn_w // 2
        spacing = 60
        base_y = 360

        self.buttons = [
            Button("PLAY",    self.font_large, btn_x, base_y,             btn_w, btn_h, (30, 0, 80), (80, 0, 180)),
            Button("HISTORY", self.font_large, btn_x, base_y + spacing,   btn_w, btn_h, (30, 0, 80), (80, 0, 180)),
            Button("CREDITS", self.font_large, btn_x, base_y + spacing*2, btn_w, btn_h, (30, 0, 80), (80, 0, 180)),
            Button("QUIT",    self.font_large, btn_x, base_y + spacing*3, btn_w, btn_h, (60, 0, 0),  (180, 0, 0)),
        ]

    def lerp(self, a, b, t):
        return a + (b - a) * t

    def slide_out(self):
        # call this from main.py when play is pressed to trigger slide away
        self.state = self.STATE_SLIDEOUT

    def update(self, events):
        self.timer += 1
        self.action = None

        self.flash_timer += 1
        if self.flash_timer >= 30:
            self.flash_visible = not self.flash_visible
            self.flash_timer = 0

        if self.state == self.STATE_TITLE:
            for event in events:
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = self.STATE_SLIDING

        elif self.state == self.STATE_SLIDING:
            self.logo_y   = self.lerp(self.logo_y,   self.logo_y_target_menu,      0.08)
            self.buttons_y = self.lerp(self.buttons_y, self.buttons_y_target_shown, 0.08)

            # rocket science ahh
            if abs(self.logo_y - self.logo_y_target_menu) < 1 and abs(self.buttons_y - self.buttons_y_target_shown) < 1:
                self.logo_y    = self.logo_y_target_menu
                self.buttons_y = self.buttons_y_target_shown
                self.state     = self.STATE_MENU

        elif self.state == self.STATE_MENU:
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                btn.check_hover(mouse_pos)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in self.buttons:
                        if btn.is_clicked(mouse_pos):
                            self.action = btn.text

        elif self.state == self.STATE_SLIDEOUT:
            # logo and buttons slide back down off screen
            self.logo_y    = self.lerp(self.logo_y,    self.logo_y_target_title,    0.08)
            self.buttons_y = self.lerp(self.buttons_y, self.buttons_y_target_hidden, 0.08)

            if abs(self.logo_y - self.logo_y_target_title) < 1 and abs(self.buttons_y - self.buttons_y_target_hidden) < 1:
                self.logo_y    = self.logo_y_target_title
                self.buttons_y = self.buttons_y_target_hidden
                self.action    = "SLIDEOUT_DONE"

    def draw(self, screen):
        # classic sin maths to make the planets move around
        planet_y = self.sh - 220 + math.sin(self.timer * 0.02) * 8
        screen.blit(self.planet, (30, planet_y))

        asteroid_x = 20 + math.sin(self.timer * 0.01) * 5
        screen.blit(self.asteroid, (asteroid_x, 20))

        title_bob = math.sin(self.timer * 0.03) * 4
        screen.blit(self.lunar,  (0, self.logo_y + title_bob))
        screen.blit(self.attack, (0, self.logo_y + title_bob))

        if self.state == self.STATE_TITLE and self.flash_visible:
            press_surf = self.font_small.render(">> PRESS START <<", True, (180, 180, 255))
            press_rect = press_surf.get_rect(center=(self.sw // 2, self.sh // 2 + 160))
            screen.blit(press_surf, press_rect)

        if self.state in (self.STATE_SLIDING, self.STATE_MENU, self.STATE_SLIDEOUT):
            for btn in self.buttons:
                btn.draw(screen, offset_y=self.buttons_y)