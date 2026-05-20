import math

import pygame

BULLET_SPEED = 50
BULLET_RADIUS = 5
BULLET_MAX_DISTANCE = 1500
COLOR_BULLET = (255, 255, 0)


class Bullet:
    """Bullet fired toward the mouse aim direction."""

    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.start_x = self.x
        self.start_y = self.y
        self.angle = angle
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.alive = True

    def update(self):
        if not self.alive:
            return
        self.x += self.vx
        self.y += self.vy
        traveled = math.hypot(self.x - self.start_x, self.y - self.start_y)
        if traveled >= BULLET_MAX_DISTANCE:
            self.alive = False

    def draw(self, screen, camera):
        if not self.alive:
            return
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y

        pygame.draw.circle(
            screen,
            COLOR_BULLET,
            (int(screen_x), int(screen_y)),
            BULLET_RADIUS,
        )
