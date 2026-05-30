import pygame


class Credits:
    SCROLL_SPEED = 50  # pixels per second

    LINES = [
        ("LUNAR ATTACK", "title"),
        ("A TERRA DEFENSE PRODUCTION", "subtitle"),
        ("", "gap"),
        ("─────────────────────", "divider"),
        ("", "gap"),
        ("GAME DESIGN", "heading"),
        ("Yumnu", "name"),
        ("Kenzie", "name"),
        ("Jin", "name"),
        ("Richardo", "name"),
        ("", "gap"),
        ("─────────────────────", "divider"),
        ("", "gap"),
        ("PROGRAMMING", "heading"),
        ("Yumnu", "name"),
        ("Kenzie", "name"),
        ("Jinyoung", "name"),
        ("Richardo", "name"),
        ("", "gap"),
        ("─────────────────────", "divider"),
        ("", "gap"),
        ("ART & ASSETS", "heading"),
        ("Jin", "name"),
        ("", "gap"),
        ("─────────────────────", "divider"),
        ("", "gap"),
        ("MUSIC & SOUND DESIGN", "heading"),
        ("Yumnu", "name"),
        ("Jin", "name"),
        ("Kenjie", "name"),
        ("Richardo", "name"),
        ("", "gap"),
        ("PLAY TESTING", "heading"),
        ("Simmi", "name"),
        ("", "gap"),
        ("─────────────────────", "divider"),
        ("", "gap"),
        ("SPECIAL THANKS", "heading"),
        ("Asia Pacific University", "name"),
        ("Ms Mary Ting", "name"),
        ("Ms Tan Li June", "name"),
        ("", "gap"),
        ("─────────────────────", "divider"),
        ("", "gap"),
        ("MADE WITH", "heading"),
        ("Python & Pygame", "name"),
        ("", "gap"),
        ("─────────────────────", "divider"),
        ("", "gap"),
        ("\u00a9 2026 TERRA DEFENSE", "small"),
        ("ALL RIGHTS RESERVED", "small"),
        ("", "gap"),
        ("", "gap"),
        ("", "gap"),
        ("", "gap"),
        ("", "gap"),
    ]

    FONT_SIZES = {
        "title": 20,
        "subtitle": 10,
        "heading": 11,
        "name": 9,
        "small": 7,
        "divider": 8,
        "gap": 8,
    }

    COLORS = {
        "title": (255, 215, 0),
        "subtitle": (200, 180, 100),
        "heading": (180, 180, 255),
        "name": (220, 220, 255),
        "small": (120, 120, 160),
        "divider": (80, 80, 120),
        "gap": (0, 0, 0),
    }

    LINE_SPACING = {
        "title": 48,
        "subtitle": 32,
        "heading": 36,
        "name": 28,
        "small": 24,
        "divider": 24,
        "gap": 16,
    }

    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h

        self.action = None
        self.scroll_y = float(screen_h)

        self.fonts = {
            tag: pygame.font.Font("PressStart2P-Regular.ttf", size)
            for tag, size in self.FONT_SIZES.items()
        }

        raw = pygame.image.load("imgs/MainMenu/creditsTitle.png").convert_alpha()
        self.title_img = pygame.transform.scale(raw, (screen_w, screen_h))

        raw_us = pygame.image.load("imgs/MainMenu/us.png").convert_alpha()
        self.us_img = pygame.transform.scale(raw_us, (371, 209))

        self.rendered = []
        for text, tag in self.LINES:
            if tag == "gap":
                self.rendered.append((None, tag))
            else:
                surf = self.fonts[tag].render(text, True, self.COLORS[tag])
                self.rendered.append((surf, tag))

        self.total_h = sum(self.LINE_SPACING[tag] for _, tag in self.LINES)
        self.pause_timer = 0.0

    def open(self):
        self.action = None
        self.scroll_y = float(self.sh)
        self.pause_timer = 0.0

    def update(self, dt, events):
        self.action = None

        # stop scrolling when all text has scrolled off top
        if self.scroll_y + self.total_h > 220:
            self.scroll_y -= self.SCROLL_SPEED * dt
            self.pause_timer = 0  # reset timer while still scrolling
        else:
            # count how long we've been paused
            self.pause_timer += dt
            if self.pause_timer >= 1.0:  # wait 3 seconds then go to menu
                self.action = "DONE"

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.action = "DONE"

    def draw(self, screen):
        screen.blit(self.title_img, (0, 0))

        clip_rect = pygame.Rect(0, 220, self.sw, self.sh - 220)
        screen.set_clip(clip_rect)

        cx = self.sw // 2
        y = self.scroll_y

        for (surf, tag) in self.rendered:
            spacing = self.LINE_SPACING[tag]
            if surf is not None:
                if -spacing < y < self.sh:
                    rect = surf.get_rect(centerx=cx, y=int(y))
                    screen.blit(surf, rect)
            y += spacing

        # draw us.png after all text lines, scrolls with text
        img_y = int(self.scroll_y + self.total_h)
        if 220 < img_y < self.sh:
            img_rect = self.us_img.get_rect(centerx=cx, y=img_y)
            screen.blit(self.us_img, img_rect)

        screen.set_clip(None)