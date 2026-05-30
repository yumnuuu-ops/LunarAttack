import pygame
from MainMenu import Button


class History:
    def __init__(self, screen_w, screen_h, score_manager):
        self.sw = screen_w
        self.sh = screen_h

        self.font_title = pygame.font.Font("PressStart2P-Regular.ttf", 32)
        self.font_medium = pygame.font.Font("PressStart2P-Regular.ttf", 16)
        self.font_small = pygame.font.Font("PressStart2P-Regular.ttf", 12)

        self.action = None

        self.on_hover = lambda: None
        self.on_click = lambda: None

        # title image
        raw = pygame.image.load("imgs/MainMenu/historyTitle.png").convert_alpha()
        self.title_img = pygame.transform.scale(raw, (screen_w, screen_h))

        # trophy icon
        raw_trophy = pygame.image.load("imgs/MainMenu/trophy.png").convert_alpha()
        self.trophy_img = pygame.transform.scale(raw_trophy, (20, 20))

        # back button
        btn_w = 200
        btn_h = 40
        self.btn_back = Button(
            "BACK", self.font_medium,
            screen_w // 2 - btn_w // 2, screen_h - 60,
            btn_w, btn_h,
            (30, 0, 80), (80, 0, 180)
        )

        # load and sort history
        self.score_manager = score_manager
        self._refresh()

    def _refresh(self):
        history = self.score_manager.get_history()
        self.entries = sorted(history, key=lambda e: e["score"], reverse=True)

    def update(self, events):
        self.action = None
        mouse_pos = pygame.mouse.get_pos()

        was_hovered = self.btn_back.hovered
        self.btn_back.check_hover(mouse_pos)
        if self.btn_back.hovered and not was_hovered:
            self.on_hover()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_back.is_clicked(mouse_pos):
                    self.on_click()
                    self.action = "BACK"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.action = "BACK"

    def draw(self, screen):
        # title overlay
        screen.blit(self.title_img, (0, 0))

        # entries
        start_y = 270
        row_h = 52
        pad_x = 100
        col_score = self.sw - pad_x - 160

        for i, entry in enumerate(self.entries[:10]):
            y = start_y + i * row_h
            is_best = entry.get("is_highscore", False)

            name_color = (255, 215, 0) if is_best else (200, 200, 255)
            score_color = (255, 215, 0) if is_best else (255, 255, 255)
            meta_color = (180, 140, 0) if is_best else (120, 120, 160)

            # trophy icon
            if is_best:
                screen.blit(self.trophy_img, (pad_x - 28, y + 2))

            # name
            name_surf = self.font_medium.render(entry["name"].upper(), True, name_color)
            screen.blit(name_surf, (pad_x, y))

            # score (right aligned)
            score_surf = self.font_medium.render(f"{entry['score']:07}", True, score_color)
            score_rect = score_surf.get_rect(right=col_score + 160, y=y)
            screen.blit(score_surf, score_rect)

            # difficulty + date (smaller, below name)
            meta_text = f"{entry['difficulty'].upper()}   {entry.get('date', '')}"
            meta_surf = self.font_small.render(meta_text, True, meta_color)
            screen.blit(meta_surf, (pad_x, y + 20))

            # separator line
            if i < len(self.entries) - 1:
                line_color = (100, 80, 0) if is_best else (40, 40, 60)
                pygame.draw.line(screen, line_color,
                                 (pad_x, y + row_h - 6),
                                 (self.sw - pad_x, y + row_h - 6), 1)

        # back button
        self.btn_back.draw(screen)