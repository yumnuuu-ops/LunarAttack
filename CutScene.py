

import pygame

class CutScene:
    STATE_FADEIN  = "fadein"
    STATE_TYPING  = "typing"
    STATE_WAIT    = "wait"
    STATE_FADEOUT = "fadeout"
    STATE_BANDOUT = "bandout"  # new state for fading the band away at the end

    def __init__(self, screen_w, screen_h, player_name="Cadet"):
        self.sw = screen_w
        self.sh = screen_h

        self.font       = pygame.font.Font("PressStart2P-Regular.ttf", 12)
        self.font_small = pygame.font.Font("PressStart2P-Regular.ttf", 10)


        self.img_w = 371
        self.img_h = 209

        self.img_alpha  = 0
        self.fade_speed = 4

        self.current_line    = 0
        self.current_char    = 0
        self.type_timer      = 0
        self.type_speed      = 2
        self.displayed_lines = []
        self.typing_done     = False

        self.flash_timer   = 0
        self.flash_visible = True

        self.scene_index = 0
        self.state       = self.STATE_FADEIN
        self.action      = None

        self.img_surface = pygame.Surface((self.img_w, self.img_h))

        self.player_name = player_name

        # band starts fully visible, fades away only at the very end
        self.band_alpha = 255

        self.skip_hold_timer = 0
        self.skip_hold_required = 90

        self.scenes = [
            {
                "image"  : "imgs/Narration/nMoon.png",
                "layout" : "text_left",
                "lines"  : [
                    "It is the year 3067.",
                    "There has been signs of something lurking in the night sky.",#there is something lurking in the night sky
                    "The Moon... ever so slightly has shifted.",
                    "Gone were the days of the waxing moon",
                    "Something ancient and corrupt has taken hold of it.",
                ],
                "sound"  : "moon_ambient",
                "size": (371, 209)
            },
            {
                "image"  : "imgs/Narration/nSea.png",
                "layout" : "image_left",
                "lines"  : [
                    "It all started slowly,",
                    "Strange tides...",
                    "Unexplained earthquakes..",
                    "Sunken Ships..",
                ],
                "sound"  : "sea_storm",
                "size": (209, 371)
            },
            {#nuclear explosioin image
                "image"  : "imgs/Narration/nAttack.png",
                "layout" : "text_left",
                "lines"  : [
                    "Suddenly one day..",
                    "tremors are felt all over the world..",
                    "The distorted reflection of the moonlight..",
                    "accompanied by its rage, now is shining upon us...",
                ],
                "sound"  : "explosion",
                "size": (371, 209)
            },
            {#hopeless government
                "image"  : "imgs/Narration/nGovernment.png",
                "layout" : "image_left",
                "lines"  : [
                    "There are no longer people in charge..",
                    "Governments are a thing of the past..",
                    "The Terra Defence Program",
                    "the last frontier..",
                    "Held its last meeting.",
                ],
                "sound"  : "government_tension",
                "size": (371, 209)

            },
            {#rockets flying up
                "image"  : "imgs/Narration/nTerraDefense.png",
                "layout" : "text_left",
                "lines"  : [
                    f"You... {self.player_name}.",  #username,
                    "Our bravest soldier.",
                    "Everyone we sent before you",
                    "did not return...",
                    "You are different..",
                    "This ends today!!",
                ],
                "sound"  : "launch",
                "size": (371, 209)
            },
            {
                "image"  : "imgs/Narration/nEarth.png",
                "layout" : "image_left",
                "lines"  : [
                    "The twisted corruption shall fall.", #The corruption sha
                    "and Moon light will shine upon us once again.",
                    "Suit up soldier",
                    "This will be your final mission.",
                    "Fall. and the end is nigh..",
                ],
                "sound"  : "epic_swell",
                "size"  :   (371,209)
            },
        ]

        self._load_scene(0)

    def _load_scene(self, index):
        scene = self.scenes[index]

        size = scene.get("size", (self.img_w, self.img_h))
        raw = pygame.image.load(scene["image"]).convert_alpha()
        self.img_surface = pygame.transform.scale(raw, size)

        self.img_alpha       = 0
        self.current_line    = 0
        self.current_char    = 0
        self.type_timer      = 0
        self.displayed_lines = []
        self.typing_done     = False
        self.state           = self.STATE_FADEIN
        # band stays at 255 between scenes, only fades at the very end
        self.band_alpha      = 255

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
        if not self.typing_done:
            # skip typewriter, show all lines instantly
            scene = self.scenes[self.scene_index]
            self.displayed_lines = list(scene["lines"])
            self.current_line    = len(scene["lines"])
            self.current_char    = 0
            self.typing_done     = True
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
                        if self.skip_hold_timer < 5:  # only advance if not already holding
                            self._advance()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state in (self.STATE_TYPING, self.STATE_WAIT):
                    if self.skip_hold_timer < 5:
                        self._advance()

        # long hold skip
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        if keys[pygame.K_SPACE] or mouse[0]:
            self.skip_hold_timer += 1
            if self.skip_hold_timer >= self.skip_hold_required:
                self.skip_hold_timer = self.skip_hold_required  # cap it so bar stays full
                if self.state != self.STATE_BANDOUT:  # only trigger once
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
        # during band fadeout, still draw the band fading away
        if self.state == self.STATE_BANDOUT or self.scene_index >= len(self.scenes):
            band_h    = 420
            band_y    = (self.sh - band_h) // 2
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

        # black middle band
        band_h    = 420
        band_y    = (self.sh - band_h) // 2
        band_surf = pygame.Surface((self.sw, band_h))
        band_surf.fill((5, 5, 15))
        band_surf.set_alpha(self.band_alpha)
        screen.blit(band_surf, (0, band_y))

        # image with fade
        faded = self.img_surface.copy()
        faded.set_alpha(self.img_alpha)
        screen.blit(faded, img_rect)

        # image border
        pygame.draw.rect(screen, (80, 80, 120), img_rect, 2)

        # completed lines
        line_h  = 22
        drawn_y = text_y
        for line in self.displayed_lines:
            surf = self.font.render(line, True, (200, 200, 255))
            screen.blit(surf, (text_x, drawn_y))
            drawn_y += line_h

        # currently typing line
        if self.current_line < len(scene["lines"]) and self.state == self.STATE_TYPING:
            partial = scene["lines"][self.current_line][:self.current_char]
            surf    = self.font.render(partial, True, (255, 255, 255))
            screen.blit(surf, (text_x, drawn_y))

        # space prompt
        if self.typing_done and self.flash_visible:
            is_last = self.scene_index >= len(self.scenes) - 1
            prompt  = "[ SPACE ] to end" if is_last else "[ SPACE ] to continue"
            prompt_surf = self.font_small.render(prompt, True, (140, 140, 200))
            screen.blit(prompt_surf, (text_x, text_y + line_h * 8))

            # skip hold progress bar
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
        # scene counter
        counter = self.font_small.render(
            f"{self.scene_index + 1} / {len(self.scenes)}", True, (80, 80, 100)
        )
        screen.blit(counter, (self.sw - 80, self.sh - 30))