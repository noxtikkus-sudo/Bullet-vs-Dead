import math

import pygame

from entity import CircleEntity
from settings import (
    COLOR_PLAYER,
    COLOR_PLAYER_AIM,
    DIAGONAL_SCALE,
    PLAYER_AIM_LENGTH,
    PLAYER_AIM_WIDTH,
    PLAYER_DAMAGE_COOLDOWN,
    PLAYER_MAX_HP,
    PLAYER_RADIUS,
    PLAYER_SPEED,
)
from utils import tick_down


class Player(CircleEntity):
    def __init__(self):
        super().__init__(0, 0, PLAYER_RADIUS, PLAYER_MAX_HP)
        self.angle = 0.0
        self._damage_cooldown = 0.0

    def take_damage(self, amount):
        if not self.alive or self._damage_cooldown > 0:
            return
        self.hp -= amount
        self._damage_cooldown = PLAYER_DAMAGE_COOLDOWN
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, camera, dt, game_map):
        self._damage_cooldown = tick_down(self._damage_cooldown, dt)
        if not self.alive:
            return

        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * PLAYER_SPEED
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * PLAYER_SPEED
        if dx and dy:
            dx *= DIAGONAL_SCALE
            dy *= DIAGONAL_SCALE

        self.x, self.y = game_map.resolve_circle_move(
            self.x, self.y, self.radius, dx, dy, for_enemy=False
        )

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.angle = math.atan2(
            mouse_y + camera.y - self.y,
            mouse_x + camera.x - self.x,
        )

    def draw(self, screen, camera):
        self.draw_circle(screen, camera, COLOR_PLAYER)
        if not self.alive:
            return

        screen_x = self.x - camera.x
        screen_y = self.y - camera.y
        aim_x = screen_x + math.cos(self.angle) * PLAYER_AIM_LENGTH
        aim_y = screen_y + math.sin(self.angle) * PLAYER_AIM_LENGTH
        pygame.draw.line(
            screen,
            COLOR_PLAYER_AIM,
            (screen_x, screen_y),
            (aim_x, aim_y),
            PLAYER_AIM_WIDTH,
        )
