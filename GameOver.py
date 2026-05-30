import pygame
from MainMenu import Button


class GameOver:
    SHATTER_WAIT  = 1.5   # seconds to let shatter play before fading in / i would like to make this dynamic
    FADE_SPEED    = 3      # alpha increment per frame (255 / 3 ≈ 85 frames ≈ 1.4s at 60fps)

    def __init__(self, screen_w, screen_h, player_name, score):
        self.sw          = screen_w
        self.sh          = screen_h
        self.player_name = player_name
        self.score       = score

        self.font_name  = pygame.font.Font("PressStart2P-Regular.ttf", 10)
        self.font_score = pygame.font.Font("PressStart2P-Regular.ttf", 14)
        self.font_btn   = pygame.font.Font("PressStart2P-Regular.ttf", 11)

        # load game over image (1280x720 PNG with transparency)
        raw = pygame.image.load("imgs/MainMenu/gameOver.png").convert_alpha()
        self.image = pygame.transform.scale(raw, (screen_w, screen_h))

        # state
        self.action       = None
        self._phase       = "wait"   # wait → fade → active
        self._wait_timer  = 0.0
        self._alpha       = 0
        self._buttons_on  = False

        # callbacks
        self.on_hover = lambda: None
        self.on_click = lambda: None

        # buttons — YES and NO centered below the game over text
        cx      = screen_w // 2
        btn_w   = 200
        btn_h   = 48
        gap     = 40
        total   = btn_w * 2 + gap
        btn_y   = screen_h // 2 + 140   # below the "play again?" text on the image

        COLOR_YES       = (0,  80,  0)
        COLOR_YES_HOV   = (0, 160,  0)
        COLOR_NO        = (60,  0,  0)
        COLOR_NO_HOV    = (180, 0,  0)

        self.btn_yes = Button(
            "YES!", self.font_btn,
            cx - total // 2, btn_y,
            btn_w, btn_h,
            COLOR_YES, COLOR_YES_HOV
        )
        self.btn_no = Button(
            "NO.", self.font_btn,
            cx - total // 2 + btn_w + gap, btn_y,
            btn_w, btn_h,
            COLOR_NO, COLOR_NO_HOV
        )

        self.buttons = [self.btn_yes, self.btn_no]

    def open(self):
        self.action      = None
        self._phase      = "wait"
        self._wait_timer = 0.0
        self._alpha      = 0
        self._buttons_on = False

    def update(self, dt, events):
        self.action = None

        if self._phase == "wait":
            self._wait_timer += dt
            if self._wait_timer >= self.SHATTER_WAIT:
                self._phase = "fade"

        elif self._phase == "fade":
            self._alpha += self.FADE_SPEED
            if self._alpha >= 255:
                self._alpha      = 255
                self._phase      = "active"
                self._buttons_on = True

        elif self._phase == "active":
            mouse_pos = pygame.mouse.get_pos()

            for btn in self.buttons:
                was_hovered = btn.hovered
                btn.check_hover(mouse_pos)
                if btn.hovered and not was_hovered:
                    self.on_hover()

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_yes.is_clicked(mouse_pos):
                        self.on_click()
                        self.action = "PLAY_AGAIN"
                    elif self.btn_no.is_clicked(mouse_pos):
                        self.on_click()
                        self.action = "MENU"

    def draw(self, screen):
        if self._alpha <= 0:
            return

        # blit the game over image with current alpha
        img = self.image.copy()
        img.set_alpha(self._alpha)
        screen.blit(img, (0, 0))

        if self._alpha < 80:
            return  # don't draw text until image is somewhat visible

        # calculate text alpha (ramp in after image is mostly visible)
        text_alpha = min(255, max(0, (self._alpha - 80) * 3))

        cx = self.sw // 2

        # player name line
        name_text = f"{self.player_name}'s SCORE"
        name_surf = self.font_name.render(name_text, True, (200, 200, 255))
        name_surf.set_alpha(text_alpha)
        name_rect = name_surf.get_rect(centerx=cx, y=self.sh // 2 + 55) #asjust to move around the score
        screen.blit(name_surf, name_rect)

        # score line
        score_text = f"{self.score:07}"
        score_surf = self.font_score.render(score_text, True, (255, 80, 80))
        score_surf.set_alpha(text_alpha)
        score_rect = score_surf.get_rect(centerx=cx, y=self.sh // 2 + 85) #adjust to move around the score
        screen.blit(score_surf, score_rect)

        # buttons (only when active)
        if self._buttons_on:
            for btn in self.buttons:
                btn.draw(screen)