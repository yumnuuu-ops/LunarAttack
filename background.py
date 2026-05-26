import pygame
import random

class Background:
    def __init__(self, screen_width, screen_height):
        self.sw = screen_width
        self.sh = screen_height

        # (filename, scroll_speed) — back to front
        layer_data = [
            # ("imgs/blue-back.png", 0.3, (screen_width, screen_height)),  # this one SHOULD fill screen
            ("imgs/blue-with-stars.png", 0.9, (screen_width, screen_height)),  # and this
            ("imgs/blue-stars.png", 0.8, (screen_width, screen_height)),  # this too
            # ("imgs/prop-planet-big.png", 1.2, (300, 300)),  # planet, medium
            # ("imgs/prop-planet-small.png", 1.5, (150, 150)),  # planet, small
            # ("imgs/asteroid-1.png", 2.0, (80, 80)),  # asteroid
            # ("imgs/asteroid-2.png", 2.5, (60, 60)),  # asteroid
        ]

        self.layers = []
        for path, speed, size in layer_data:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (screen_width, screen_height))
            self.layers.append({
                "img": img,
                "speed": speed,
                "offset": 0.0,
                "x": random.randint(0, screen_width - size[0])  # random x position
            })

    def update(self, dt):
        for layer in self.layers:
            layer["offset"] = (layer["offset"] + layer["speed"] * dt * 60) % self.sh

    def draw(self, screen):
        for layer in self.layers:
            offset = layer["offset"]
            h = self.sh
            # Draw twice for seamless looping
            screen.blit(layer["img"], (0, offset - h))
            screen.blit(layer["img"], (0, offset))