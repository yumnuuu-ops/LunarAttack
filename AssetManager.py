import pygame
class AssetManager:
    def __init__(self, global_scale=1):
        self.textures = {}

        self.Animation = {}
        self.frameW = 32
        self.frameH = 32

        self.global_scale = global_scale


    def loadTexture(self, name, path):
        if not name or not path:
            return
        texture = pygame.image.load(path).convert_alpha()

        # If a scale factor other than 1 is provided, scale up
        if self.global_scale != 1:
            texture = pygame.transform.scale_by(texture, self.global_scale)

        self.textures[name] = texture
        return texture

    def getTexture(self, name):
        if not name:
            return

        if name in self.textures:
            return self.textures[name]
        else:
            print(f"Error: Texture '{name}' was never loaded!")
            return None

    def getRect(self, name):
        if not name:
            return

        if name in self.textures:
            return self.textures[name].get_rect()
        else:
            print(f"Error: Texture '{name}' was never loaded!")
            return None

    def loadAnim(self, name, path):
        if not name or not path:
            return

        # Load a sprite sheet
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        # Calculate how many frames are in the sheet
        sheet_width, sheet_height = sheet.get_size()
        num_frames = sheet_width // self.frameW

        # Slice the sheet into individual frame surfaces
        for i in range(num_frames):
            rect = pygame.Rect(i * self.frameW, 0, self.frameW, self.frameH)
            frame_surface = pygame.Surface((self.frameW, self.frameH), pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), rect)

            # Scale up if needed
            if self.global_scale != 1:
                frame_surface = pygame.transform.scale(
                    frame_surface, (self.frameW * self.global_scale, self.frameH * self.global_scale)
                )
            frames.append(frame_surface)

        self.Animation[name] = frames

    def getAnim(self, name):
        if name in self.Animation:
            return self.Animation[name]
        print(f"Error: Animation '{name}' was never loaded!")
        return None