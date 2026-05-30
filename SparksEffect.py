import math
import random

import pygame

from globals import particle_group


class SparksEffect(pygame.sprite.Sprite):
    def __init__(self, destroyed_entity, amount=42):
        super().__init__()
        self.x = destroyed_entity.rect.centerx
        self.y = destroyed_entity.rect.centery
        self.amount = amount

        self.age = 0
        self.spark_delay = 5
        self.spark_spawned = False
        self.explosion_alpha = 230
        self.explosion_radius = 10
        self.sparks = []

        self.canvas_size = 240
        self.center = pygame.math.Vector2(self.canvas_size // 2, self.canvas_size // 2)
        self.image = pygame.Surface((self.canvas_size, self.canvas_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self._draw_effect()

    def start(self):
        particle_group.add(self)

    def _create_sparks(self):
        for _ in range(self.amount):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(4.0, 9.0)
            self.sparks.append(
                {
                    "pos": self.center.copy(),
                    "velocity": pygame.math.Vector2(math.cos(angle) * speed, math.sin(angle) * speed),
                    "length": random.randint(8, 18),
                    "radius": random.randint(2, 4),
                    "alpha": 255,
                    "fade_speed": random.randint(9, 15),
                    "color": random.choice(
                        [
                            (255, 235, 110),
                            (255, 165, 45),
                            (255, 90, 40),
                            (255, 245, 220),
                        ]
                    ),
                }
            )

    def _update_sparks(self):
        for spark in self.sparks:
            spark["pos"] += spark["velocity"]
            spark["velocity"] *= 0.94
            spark["alpha"] -= spark["fade_speed"]

        self.sparks = [spark for spark in self.sparks if spark["alpha"] > 0]

    def _draw_explosion(self):
        if self.explosion_alpha <= 0:
            return

        color = (255, 165, 45, max(0, min(255, int(self.explosion_alpha))))
        inner_color = (255, 245, 210, max(0, min(255, int(self.explosion_alpha * 0.9))))
        pygame.draw.circle(self.image, color, self.center, max(1, int(self.explosion_radius)))
        pygame.draw.circle(self.image, inner_color, self.center, max(1, int(self.explosion_radius * 0.45)))

    def _draw_sparks(self):
        for spark in self.sparks:
            velocity = spark["velocity"]
            direction = velocity.normalize() if velocity.length() > 0 else pygame.math.Vector2(1, 0)
            end = spark["pos"] + direction * spark["length"]
            start = spark["pos"] - direction * spark["length"] * 0.35
            color = (*spark["color"], max(0, min(255, int(spark["alpha"]))))

            pygame.draw.line(self.image, color, start, end, spark["radius"])
            pygame.draw.circle(self.image, color, end, spark["radius"])

    def _draw_effect(self):
        self.image.fill((0, 0, 0, 0))
        self._draw_explosion()
        self._draw_sparks()

    def update(self):
        self.age += 1

        self.explosion_radius += 3
        self.explosion_alpha -= 22

        if self.age >= self.spark_delay and not self.spark_spawned:
            self._create_sparks()
            self.spark_spawned = True

        self._update_sparks()
        self._draw_effect()

        if self.explosion_alpha <= 0 and self.spark_spawned and not self.sparks:
            self.kill()
