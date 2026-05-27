import math

import pygame

from map import GameMap
from settings import BULLET_MAX_DISTANCE, BULLET_RADIUS, BULLET_SPEED, COLOR_BULLET, ENEMY_RADIUS


class Bullet:
    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.start_x = self.x
        self.start_y = self.y
        self.angle = angle
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.alive = True
        self.prev_x = self.x
        self.prev_y = self.y

    def _hit_enemy_on_step(self, x1, y1, x2, y2, enemies):
        hit_radius = ENEMY_RADIUS + BULLET_RADIUS
        hit_enemy = None
        hit_t = 2.0

        for enemy in enemies:
            if not enemy.is_alive:
                continue
            if not GameMap.segment_hits_circle(x1, y1, x2, y2, enemy.x, enemy.y, hit_radius):
                continue

            dx = x2 - x1
            dy = y2 - y1
            length_sq = dx * dx + dy * dy
            if length_sq == 0:
                t = 0.0
            else:
                t = max(0.0, min(1.0, ((enemy.x - x1) * dx + (enemy.y - y1) * dy) / length_sq))
            if t < hit_t:
                hit_t = t
                hit_enemy = enemy

        if hit_enemy is not None:
            hit_enemy.take_damage(1)
            self.alive = False
            return True
        return False

    def update(self, game_map=None, enemies=None):
        if not self.alive:
            return

        self.prev_x = self.x
        self.prev_y = self.y

        steps = max(1, math.ceil(max(abs(self.vx), abs(self.vy)) / 6))
        for _ in range(steps):
            next_x = self.x + self.vx / steps
            next_y = self.y + self.vy / steps

            if enemies and self._hit_enemy_on_step(self.x, self.y, next_x, next_y, enemies):
                return

            if game_map is not None and game_map.circle_hits_wall(
                next_x, next_y, BULLET_RADIUS
            ):
                self.alive = False
                return

            self.x = next_x
            self.y = next_y

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
