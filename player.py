import math

import pygame

from entity import CircleEntity, draw_rotated_sprite, load_sprite
from settings import (
    DIAGONAL_SCALE,
    PLAYER_DAMAGE_COOLDOWN,
    PLAYER_MAX_HP,
    PLAYER_RADIUS,
    PLAYER_SPRITE,
    PLAYER_SPRITE_SIZE,
    PLAYER_SPEED,
)
from utils import tick_down


class Player(CircleEntity):
    _sprite = None

    def __init__(self):
        super().__init__(0, 0, PLAYER_RADIUS, PLAYER_MAX_HP)
        self.angle = 0.0
        self._damage_cooldown = 0.0
        if Player._sprite is None:
            Player._sprite = load_sprite(PLAYER_SPRITE, PLAYER_SPRITE_SIZE)

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
        if not self.alive:
            return
        draw_rotated_sprite(screen, Player._sprite, self.x, self.y, camera, self.angle)
