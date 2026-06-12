import math
from pathlib import Path

import pygame

from utils import circles_overlap, to_screen


def load_sprite(filename, size):
    sprite = pygame.image.load(Path(__file__).resolve().parent / "assets" / filename).convert_alpha()
    if isinstance(size, int):
        size = (size, size)
    return pygame.transform.smoothscale(sprite, size)


def draw_rotated_sprite(screen, sprite, x, y, camera, angle):
    rotated = pygame.transform.rotate(sprite, -math.degrees(angle))
    rect = rotated.get_rect(center=to_screen(x, y, camera))
    screen.blit(rotated, rect)


class CircleEntity:
    def __init__(self, x, y, radius, hp):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.max_hp = hp
        self.hp = hp
        self.alive = True

    @property
    def is_alive(self):
        return self.alive

    def take_damage(self, amount):
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def hits_circle(self, x, y, radius):
        return circles_overlap(self.x, self.y, self.radius, x, y, radius)

    def draw_circle(self, screen, camera, color):
        if not self.alive:
            return
        pygame.draw.circle(screen, color, to_screen(self.x, self.y, camera), self.radius)
