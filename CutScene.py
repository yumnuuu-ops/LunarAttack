import pygame


class CutScene:
    STATE_FADEIN = "fadein"
    STATE_TYPING = "typing"
    STATE_WAIT = "wait"
    STATE_FADEOUT = "fadeout"
    STATE_BANDOUT = "bandout"

    COLOR_DEFAULT = (200, 200, 255)
    COLOR_TYPING = (255, 255, 255)
    COLOR_MOON = (220, 60, 60)
    COLOR_PLAYER = (50, 220, 100)

    def __init__(self, screen_w, screen_h, player_name="Cadet", scenes="intro"):
        self.sw = screen_w
        self.sh = screen_h

        self.font = pygame.font.Font("PressStart2P-Regular.ttf", 12)
        self.font_small = pygame.font.Font("PressStart2P-Regular.ttf", 10)

        self.img_w = 371
        self.img_h = 209

        self.img_alpha = 0
        self.fade_speed = 4

        self.current_line = 0
        self.current_char = 0
        self.type_timer = 0
        self.type_speed = 2
        self.displayed_lines = []
        self.typing_done = False

        self.flash_timer = 0
        self.flash_visible = True

        self.scene_index = 0
        self.state = self.STATE_FADEIN
        self.action = None

        self.img_surface = pygame.Surface((self.img_w, self.img_h))

        self.player_name = player_name

        self.band_alpha = 255

        self.skip_hold_timer = 0
        self.skip_hold_required = 90

        self.on_advance = lambda: None

        self.intro_scenes = [
            {
                "image": "imgs/Narration/nMoon.png",
                "layout": "text_left",
                "lines": [
                    "It is the year 3067.",
                    "The night sky hasn't been forgiving as it used to be.",
                    "No... it brings terror to the people of earth.",
                    "Cities that once gazed at the Moon in wonder...",
                    "now hide from its glow..",
                ],
                "sound": "moon_ambient",
                "size": (371, 209)
            },
            {
                "image": "imgs/Narration/nSea.png",
                "layout": "image_left",
                "lines": [
                    "It all started slowly,",
                    "Strange tides...",
                    "Unexplained earthquakes..",
                    "Sunken Ships..",
                ],
                "sound": "sea_storm",
                "size": (209, 371)
            },
            {
                "image": "imgs/Narration/nAttack.png",
                "layout": "text_left",
                "lines": [
                    "Suddenly one day..",
                    "The attacks began!",
                    "The distorted reflection of the moonlight..",
                    "accompanied by its rage, casting evil upon us...",
                    "THE MOON HAS GONE BAD!!"
                ],
                "sound": "explosion",
                "size": (371, 209)
            },
            {
                "image": "imgs/Narration/nGovernment.png",
                "layout": "image_left",
                "lines": [
                    "Governments are a thing of the past..",
                    "No one has the guts nor the man power",
                    "to go against the Moon herself",
                ],
                "sound": "government_tension",
                "size": (371, 209)
            },
            {
                "image": "imgs/Narration/nTerraDefense.png",
                "layout": "text_left",
                "lines": [
                    f"Except for You... {player_name}!!",
                    "Our bravest soldier.",
                    "Everyone in Terra Defense sent before you",
                    "did not return...",
                    "You are different.. You WILL come back AND avenge your fallen!",
                ],
                "sound": "launch",
                "size": (371, 209)
            },
            {
                "image": "imgs/Narration/nEarth.png",
                "layout": "image_left",
                "lines": [
                    "The MOON shall be cleansed of its corruption..",
                    f"{player_name}..",
                    "Suit up soldier.",
                    "This will be your final mission.",
                    "FIGHT!!",
                ],
                "sound": "epic_swell",
                "size": (371, 209)
            },
        ]

        self.ending_scenes = [
            {
                "image": "imgs/Narration/nMoon2.png",
                "layout": "text_left",
                "lines": [
                    "The Moon is silent..?",
                    "For the first time in years..",
                ],
                "sound": "",
                "size": (371, 209)
            },
            {
                "image": "imgs/Narration/nCelebrate.png",
                "layout": "image_left",
                "lines": [
                    "We have been saved!",
                    "People can look up at the sky.. without fear.",
                    f"You did it {player_name}!!!",
                ],
                "sound": "",
                "size": (371, 209)
            },
            {
                "image": "imgs/Narration/nSalute.png",
                "layout": "text_left",
                "lines": [
                    "Our Moon is back to its former self.",
                    "Terra Defense will never forget this.",
                    "We are eternally grateful for your service.",
                    "Rest now, soldier.",
                    "You've earned it.",
                ],
                "sound": "",
                "size": (371, 209)
            },
            {
                "image": "imgs/apcard.png",
                "layout": "text_left",
                "lines": [
                    "As a token of our appreciation..",
                    "we have wired 21 Ringgit",
                    "to your AP CARD!",
                    "$$$..",
                ],
                "sound": "",
                "size": (371, 209)
            },
        ]

        self.scenes = self.ending_scenes if scenes == "ending" else self.intro_scenes

        self._load_scene(0)

    # ------------------------------------------------------------------ #
    #  Coloured line renderer                                              #
    # ------------------------------------------------------------------ #
    def _render_colored_line(self, screen, line, x, y, base_color):
        """Render a line word-by-word, colouring Moon red and player name green."""
        # Full-line overrides first
        if line in ("THE MOON HAS GONE BAD!!", "THE MOON HAS GONE BAD!!"):
            surf = self.font.render(line, True, self.COLOR_MOON)
            screen.blit(surf, (x, y))
            return

        words = line.split(" ")
        cursor = x
        space_w = self.font.size(" ")[0]

        for i, word in enumerate(words):
            # Determine color for this word
            bare = word.strip(".,!?\"'")
            if bare in ("Moon", "MOON", "moonlight"):
                color = self.COLOR_MOON
            elif self.player_name and bare == self.player_name.strip(".,!?\"'"):
                color = self.COLOR_PLAYER
            elif self.player_name and self.player_name in word:
                color = self.COLOR_PLAYER
            else:
                color = base_color

            surf = self.font.render(word, True, color)
            screen.blit(surf, (cursor, y))
            cursor += surf.get_width() + space_w

    def _render_colored_partial(self, screen, line, char_count, x, y):
        """Render a partial (typewriter) line with colouring."""
        partial = line[:char_count]
        # Work out which words are fully or partially typed
        words = line.split(" ")
        space_w = self.font.size(" ")[0]
        cursor = x
        remaining = char_count

        for word in words:
            if remaining <= 0:
                break
            chunk = word[:remaining]
            remaining -= len(word) + 1  # +1 for the space

            bare = chunk.strip(".,!?\"'")
            full_bare = word.strip(".,!?\"'")

            if full_bare in ("Moon", "MOON", "moonlight"):
                color = self.COLOR_MOON
            elif self.player_name and self.player_name in word:
                color = self.COLOR_PLAYER
            else:
                color = self.COLOR_TYPING

            surf = self.font.render(chunk, True, color)
            screen.blit(surf, (cursor, y))
            cursor += self.font.size(word)[0] + space_w

    # ------------------------------------------------------------------ #

    def _load_scene(self, index):
        scene = self.scenes[index]

        size = scene.get("size", (self.img_w, self.img_h))
        raw = pygame.image.load(scene["image"]).convert_alpha()
        self.img_surface = pygame.transform.scale(raw, size)

        self.img_alpha = 0
        self.current_line = 0
        self.current_char = 0
        self.type_timer = 0
        self.displayed_lines = []
        self.typing_done = False
        self.state = self.STATE_FADEIN
        self.band_alpha = 255

    def _get_layout(self):
        scene = self.scenes[self.scene_index]
        padding = 60

        img_w = self.img_surface.get_width()
        img_h = self.img_surface.get_height()
        img_y = self.sh // 2 - img_h // 2

        if scene["layout"] == "text_left":
            img_x = self.sw - img_w - padding
            text_x = padding
        else:
            img_x = padding
            text_x = self.sw // 2 + padding // 2

        img_rect = pygame.Rect(img_x, img_y, img_w, img_h)
        return img_rect, text_x, self.sh // 2 - 80

    def _advance(self):
        self.on_advance()
        if not self.typing_done:
            scene = self.scenes[self.scene_index]
            self.displayed_lines = list(scene["lines"])
            self.current_line = len(scene["lines"])
            self.current_char = 0
            self.typing_done = True
        else:
            self.state = self.STATE_FADEOUT

    def update(self, events):
        self.action = None

        self.flash_timer += 1
        if self.flash_timer >= 30:
            self.flash_visible = not self.flash_visible
            self.flash_timer = 0

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state in (self.STATE_TYPING, self.STATE_WAIT):
                        if self.skip_hold_timer < 5:
                            self._advance()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state in (self.STATE_TYPING, self.STATE_WAIT):
                    if self.skip_hold_timer < 5:
                        self._advance()

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        if keys[pygame.K_SPACE] or mouse[0]:
            self.skip_hold_timer += 1
            if self.skip_hold_timer >= self.skip_hold_required:
                self.skip_hold_timer = self.skip_hold_required
                if self.state != self.STATE_BANDOUT:
                    self.state = self.STATE_BANDOUT
                    self.band_alpha = 255
                    self.scene_index = len(self.scenes)
        else:
            self.skip_hold_timer = 0

        if self.state == self.STATE_BANDOUT:
            self.band_alpha = max(0, self.band_alpha - self.fade_speed * 2)
            if self.band_alpha <= 0:
                self.action = "DONE"
            return

        if self.scene_index >= len(self.scenes):
            return

        scene = self.scenes[self.scene_index]

        if self.state == self.STATE_FADEIN:
            self.img_alpha = min(255, self.img_alpha + self.fade_speed * 3)
            if self.img_alpha >= 255:
                self.img_alpha = 255
                self.state = self.STATE_TYPING

        elif self.state == self.STATE_TYPING:
            if self.current_line < len(scene["lines"]):
                self.type_timer += 1
                if self.type_timer >= self.type_speed:
                    self.type_timer = 0
                    line = scene["lines"][self.current_line]
                    if self.current_char < len(line):
                        self.current_char += 1
                    else:
                        self.displayed_lines.append(line)
                        self.current_line += 1
                        self.current_char = 0
            else:
                self.typing_done = True
                self.state = self.STATE_WAIT

        elif self.state == self.STATE_FADEOUT:
            self.img_alpha = max(0, self.img_alpha - self.fade_speed * 3)
            if self.img_alpha <= 0:
                self.scene_index += 1
                if self.scene_index >= len(self.scenes):
                    self.state = self.STATE_BANDOUT
                else:
                    self._load_scene(self.scene_index)

    def draw(self, screen):
        # Band fadeout at end
        if self.state == self.STATE_BANDOUT or self.scene_index >= len(self.scenes):
            band_h = 420
            band_y = (self.sh - band_h) // 2
            band_surf = pygame.Surface((self.sw, band_h))
            band_surf.fill((5, 5, 15))
            band_surf.set_alpha(self.band_alpha)
            screen.blit(band_surf, (0, band_y))

            if self.skip_hold_timer > 0:
                bar_w = 200
                bar_h = 6
                bar_x = self.sw // 2 - bar_w // 2
                bar_y = self.sh - 30
                fill_w = int((self.skip_hold_timer / self.skip_hold_required) * bar_w)
                pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
                pygame.draw.rect(screen, (180, 180, 255), (bar_x, bar_y, fill_w, bar_h), border_radius=3)
                label = self.font_small.render("HOLD TO SKIP", True, (140, 140, 200))
                screen.blit(label, label.get_rect(centerx=self.sw // 2, bottom=bar_y - 4))
            return

        scene = self.scenes[self.scene_index]
        img_rect, text_x, text_y = self._get_layout()

        # Black middle band
        band_h = 420
        band_y = (self.sh - band_h) // 2
        band_surf = pygame.Surface((self.sw, band_h))
        band_surf.fill((5, 5, 15))
        band_surf.set_alpha(self.band_alpha)
        screen.blit(band_surf, (0, band_y))

        # Image with fade
        faded = self.img_surface.copy()
        faded.set_alpha(self.img_alpha)
        screen.blit(faded, img_rect)

        # Image border
        pygame.draw.rect(screen, (80, 80, 120), img_rect, 2)

        # Completed lines — coloured
        line_h = 22
        drawn_y = text_y
        for line in self.displayed_lines:
            self._render_colored_line(screen, line, text_x, drawn_y, self.COLOR_DEFAULT)
            drawn_y += line_h

        # Currently typing line — coloured partial
        if self.current_line < len(scene["lines"]) and self.state == self.STATE_TYPING:
            line = scene["lines"][self.current_line]
            self._render_colored_partial(screen, line, self.current_char, text_x, drawn_y)

        # Space prompt
        if self.typing_done and self.flash_visible:
            is_last = self.scene_index >= len(self.scenes) - 1
            prompt = "[ SPACE ] to end" if is_last else "[ SPACE ] to continue"
            prompt_surf = self.font_small.render(prompt, True, (140, 140, 200))
            screen.blit(prompt_surf, (text_x, text_y + line_h * 8))

        # Skip hold progress bar
        if self.skip_hold_timer > 0:
            bar_w = 200
            bar_h = 6
            bar_x = self.sw // 2 - bar_w // 2
            bar_y = self.sh - 30
            fill_w = int((self.skip_hold_timer / self.skip_hold_required) * bar_w)
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
            pygame.draw.rect(screen, (180, 180, 255), (bar_x, bar_y, fill_w, bar_h), border_radius=3)
            label = self.font_small.render("HOLD TO SKIP", True, (140, 140, 200))
            screen.blit(label, label.get_rect(centerx=self.sw // 2, bottom=bar_y - 4))

        # Scene counter
        counter = self.font_small.render(
            f"{self.scene_index + 1} / {len(self.scenes)}", True, (80, 80, 100)
        )
        screen.blit(counter, (self.sw - 80, self.sh - 30))