import math

import pygame

from settings import (
    BULLET_DAMAGE,
    BULLET_MAX_DISTANCE,
    BULLET_MOVE_STEPS,
    BULLET_RADIUS,
    BULLET_SPEED,
    COLOR_BULLET,
)
from utils import distance, to_screen


class Bullet:
    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.start_x = self.x
        self.start_y = self.y
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.alive = True

    def update(self, game_map, enemies):
        if not self.alive:
            return

        for _ in range(BULLET_MOVE_STEPS):
            next_x = self.x + self.vx / BULLET_MOVE_STEPS
            next_y = self.y + self.vy / BULLET_MOVE_STEPS

            for enemy in enemies:
                if enemy.is_alive and enemy.hits_circle(next_x, next_y, BULLET_RADIUS):
                    enemy.take_damage(BULLET_DAMAGE)
                    self.alive = False
                    return

            if game_map.circle_hits_wall(next_x, next_y, BULLET_RADIUS):
                self.alive = False
                return

            self.x = next_x
            self.y = next_y

        if distance(self.start_x, self.start_y, self.x, self.y) >= BULLET_MAX_DISTANCE:
            self.alive = False

    def draw(self, screen, camera):
        if not self.alive:
            return
        pygame.draw.circle(screen, COLOR_BULLET, to_screen(self.x, self.y, camera), BULLET_RADIUS)
