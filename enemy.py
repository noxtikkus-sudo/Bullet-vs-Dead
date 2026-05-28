import math

import pygame

from settings import COLOR_ENEMY, ENEMY_HP, ENEMY_RADIUS, ENEMY_SPEED


class Enemy:
    """Зомби: идёт к игроку, получает урон, рисуется с учётом камеры."""

    def __init__(self, x, y, hp=None):
        self.x = float(x)
        self.y = float(y)
        self.hp = ENEMY_HP if hp is None else hp
        self.alive = True

    @property
    def is_alive(self):
        return self.alive

    def update(self, player, game_map=None):
        if not self.alive:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        length = math.hypot(dx, dy)
        if length == 0:
            return

        step = min(ENEMY_SPEED, length)
        move_x = dx / length * step
        move_y = dy / length * step

        self.x, self.y = game_map.resolve_circle_move(
            self.x, self.y, ENEMY_RADIUS, move_x, move_y, for_enemy=True
        )

    def draw(self, screen, camera):
        if not self.alive:
            return

        screen_x = int(self.x - camera.x)
        screen_y = int(self.y - camera.y)
        pygame.draw.circle(
            screen,
            COLOR_ENEMY,
            (screen_x, screen_y),
            ENEMY_RADIUS,
        )

    def take_damage(self, amount=1):
        if not self.alive:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def hits_circle(self, x, y, radius):
        """Пересечение врага с кругом в точке (x, y) с заданным радиусом."""
        return math.hypot(x - self.x, y - self.y) <= ENEMY_RADIUS + radius
