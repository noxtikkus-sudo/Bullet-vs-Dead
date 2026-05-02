import math

import pygame

from settings import BULLET_RADIUS, BULLET_SPEED, COLOR_BULLET


class Bullet:
    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y

        pygame.draw.circle(
            screen,
            COLOR_BULLET,
            (int(screen_x), int(screen_y)),
            BULLET_RADIUS,
        )

