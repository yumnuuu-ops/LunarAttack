import pygame
from MainMenu import Button

class PauseMenu:
    STATE_MENU  = "menu"
    STATE_CONFIRM = "confirm"

    def __init__(self, screen_w, screen_h):
        self.sw =screen_w
        self.sh =screen_h
        self.state = self.STATE_MENU

        self.font_title = pygame.font.Font("PressStart2P-Regular.ttf",16)
        self.font_medium = pygame.font.Font("PressStart2P-Regular.ttf", 11)
        self.font_small = pygame.font.Font("PressStart2P-Regular.ttf", 8)

        self.action = None

        self.on_hover = lambda: None
        self.on_click = lambda: None

        cx = self.sw // 2
        btn_w   = 280
        btn_h = 44
        btn_x = cx - btn_w // 2
        spacing = 56

        base_y = 260

        COLOR_BTN = (30,0,80)
        COLOR_BTN_HOVER = (80, 0, 180)
        COLOR_QUIT = (60, 0, 0)
        COLOR_QUIT_HOVER = (180, 0, 0)
        COLOR_CONFIRM = (0,80,0)
        COLOR_CONFIRM_HOVER = (0,160,0)
        COLOR_CANCEL = (60,0,0)
        COLOR_CANCEL_HOVER = (180,0,0)

        self.btn_resume = Button("RESUME", self.font_medium, btn_x, base_y, btn_w, btn_h, COLOR_BTN, COLOR_BTN_HOVER)
        self.btn_restart = Button("RESTART", self.font_medium, btn_x, base_y + spacing, btn_w, btn_h, COLOR_BTN,
                                  COLOR_BTN_HOVER)
        self.btn_menu = Button("RETURN TO MENU", self.font_medium, btn_x, base_y + spacing * 2, btn_w, btn_h, COLOR_BTN,
                               COLOR_BTN_HOVER)
        self.btn_quit = Button("QUIT GAME", self.font_medium, btn_x, base_y + spacing * 3, btn_w, btn_h, COLOR_QUIT,
                               COLOR_QUIT_HOVER)

        self.main_buttons = [
            self.btn_resume,
            self.btn_restart,
            self.btn_menu,
            self.btn_quit,
        ]

        popup_w = 500
        popup_h = 180
        self.popup_rect = pygame.Rect(cx - popup_w // 2,
                                      self.sh // 2- popup_h //2, popup_w, popup_h)

        conf_btn_w  = 160
        conf_btn_h = 40

        gap = 30
        total = conf_btn_w * 2 + gap
        conf_y = self.popup_rect.bottom - conf_btn_h - 24

        self.btn_yes = Button("YES", self.font_medium,
                              cx - total // 2, conf_y,
                              conf_btn_w, conf_btn_h, COLOR_CONFIRM, COLOR_CONFIRM_HOVER)
        self.btn_no = Button("NO", self.font_medium,
                             cx - total // 2 + conf_btn_w + gap, conf_y,
                             conf_btn_w, conf_btn_h, COLOR_CANCEL, COLOR_CANCEL_HOVER)

        self.confirm_buttons = [self.btn_yes, self.btn_no]

        self.confirm_target = None
        self.block_clicks = False

    def open(self):
        self.state = self.STATE_MENU
        self.action = None
        self.confirm_target = None
        self.block_clicks = True


    def update(self, events):
        if self.block_clicks:
            self.block_clicks = False
            return
        self.action = None
        mouse_pos = pygame.mouse.get_pos()

        if self.state == self.STATE_MENU:
            for btn in self.main_buttons:
                was_hovered = btn.hovered
                btn.check_hover(mouse_pos)
                if btn.hovered and not was_hovered:
                    self.on_hover()

            for event in events:
                #main handles the ESCAPE KEY PRESS NOW CAUSE I COULD NOT FOR THE LOVEW OF GOD GET IT TO WORK

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_resume.is_clicked(mouse_pos):
                        self.on_click()
                        self.action = "RESUME"

                    elif self.btn_restart.is_clicked(mouse_pos):
                        self.on_click()
                        self.confirm_target = "RESTART"
                        self.state = self.STATE_CONFIRM
                        self.block_clicks = True

                    elif self.btn_menu.is_clicked(mouse_pos):
                        self.on_click()
                        self.confirm_target = "MENU"
                        self.state = self.STATE_CONFIRM
                        self.block_clicks = True

                    elif self.btn_quit.is_clicked(mouse_pos):
                        self.on_click()
                        self.confirm_target = "QUIT"
                        self.state=self.STATE_CONFIRM
                        self.block_clicks = True

        elif self.state == self.STATE_CONFIRM:
            for btn in self.confirm_buttons:
                was_hovered = btn.hovered
                btn.check_hover(mouse_pos)
                if btn.hovered and not was_hovered:
                    self.on_hover()

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_MENU

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.btn_yes.is_clicked(mouse_pos):
                        self.on_click()
                        self.action = self.confirm_target
                    elif self.btn_no.is_clicked(mouse_pos):
                        self.on_click()
                        self.state = self.STATE_MENU

    def draw(self, screen):
        overlay = pygame.Surface((self.sw, self.sh))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))
        screen.blit(overlay,(0,0))

        if self.state == self.STATE_MENU:
            title = self.font_title.render("PAUSED", True, (200,200,255))
            screen.blit(title, title.get_rect(centerx=self.sw // 2, y =180))

            for btn in self.main_buttons:
                btn.draw(screen)

        elif self.state == self.STATE_CONFIRM:
            dim = pygame.Surface((self.sw, self.sh))
            dim.set_alpha(100)
            dim.fill((0,0,0))
            screen.blit(dim, (0,0))

            popup_surf = pygame.Surface((self.popup_rect.width, self.popup_rect.height))
            popup_surf.fill((10,0,30))
            screen.blit(popup_surf, self.popup_rect.topleft)
            pygame.draw.rect(screen, (80,80,120), self.popup_rect, 2, border_radius = 8)

            line1 = self.font_small.render("Your progress will not be saved.", True, (220, 180, 50))
            line2 = self.font_small.render("Are you sure?", True, (255, 255, 255))
            screen.blit(line1, line1.get_rect(centerx=self.sw // 2, y=self.popup_rect.top + 30))
            screen.blit(line2, line2.get_rect(centerx=self.sw // 2, y=self.popup_rect.top + 60))

            for btn in self.confirm_buttons:
                btn.draw(screen)