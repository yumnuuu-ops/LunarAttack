import pygame
class AssetManager:
    def __init__(self):
        self.textures = {}

    def loadTexture(self, name, path, scale=1):
        if not name or not path:
            return
        texture = pygame.image.load(path).convert_alpha()

        # If a scale factor other than 1 is provided, scale up
        if scale != 1:
            texture = pygame.transform.scale_by(texture, scale)

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