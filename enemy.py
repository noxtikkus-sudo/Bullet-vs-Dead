import math

import pygame

from entity import CircleEntity, draw_rotated_sprite, load_sprite
from settings import (
    ENEMY_HP,
    ENEMY_RADIUS,
    ENEMY_REPATH_TIME,
    ENEMY_SPEED,
    ENEMY_SPRITE,
    ENEMY_SPRITE_SIZE,
    ENEMY_WAYPOINT_REACH,
)
from utils import distance, normalize_move, tick_down, to_screen


ENEMY_HIT_TINT = (55, 20, 10, 0)
ENEMY_HIT_FLASH_TIME = 0.15
ENEMY_HP_BAR_WIDTH = 28
ENEMY_HP_BAR_HEIGHT = 4
ENEMY_HP_BAR_OFFSET = ENEMY_SPRITE_SIZE // 2 + 8
ENEMY_HP_BAR_BG = (70, 20, 20)
ENEMY_HP_BAR_FILL = (220, 40, 40)


class Enemy(CircleEntity):
    _sprite = None

    def __init__(self, x, y):
        super().__init__(x, y, ENEMY_RADIUS, ENEMY_HP)
        self.path = []
        self.path_index = 0
        self.repath_timer = 0.0
        self.hit_flash = 0.0
        self.angle = 0.0
        if Enemy._sprite is None:
            Enemy._sprite = load_sprite(ENEMY_SPRITE, ENEMY_SPRITE_SIZE)

    def take_damage(self, amount):
        was_alive = self.alive
        super().take_damage(amount)
        if was_alive:
            self.hit_flash = ENEMY_HIT_FLASH_TIME

    def _move_toward(self, target_x, target_y, game_map):
        move_x, move_y = normalize_move(target_x - self.x, target_y - self.y, ENEMY_SPEED)
        if move_x == 0 and move_y == 0:
            return
        self.angle = math.atan2(move_y, move_x)
        self.x, self.y = game_map.resolve_circle_move(
            self.x, self.y, self.radius, move_x, move_y, for_enemy=True
        )

    def update(self, player, game_map, dt, navgrid, pathfinder):
        self.hit_flash = tick_down(self.hit_flash, dt)
        if not self.alive:
            return

        self.repath_timer -= dt
        if self.repath_timer <= 0 or self.path_index >= len(self.path):
            start = navgrid.world_to_cell(self.x, self.y)
            goal = navgrid.world_to_cell(player.x, player.y)
            self.path = pathfinder.find_path(navgrid, start, goal)
            self.path_index = 1 if len(self.path) > 1 else 0
            self.repath_timer = ENEMY_REPATH_TIME

        if self.path and self.path_index < len(self.path):
            wx, wy = navgrid.cell_to_world(self.path[self.path_index])
            self._move_toward(wx, wy, game_map)
            if distance(self.x, self.y, wx, wy) < ENEMY_WAYPOINT_REACH:
                self.path_index += 1
        else:
            self._move_toward(player.x, player.y, game_map)

    def draw(self, screen, camera):
        if not self.alive:
            return
        sprite = Enemy._sprite
        if self.hit_flash > 0:
            sprite = sprite.copy()
            sprite.fill(ENEMY_HIT_TINT, special_flags=pygame.BLEND_RGBA_ADD)
        draw_rotated_sprite(screen, sprite, self.x, self.y, camera, self.angle)
        self._draw_hp_bar(screen, camera)

    def _draw_hp_bar(self, screen, camera):
        if not self.alive or self.hp >= self.max_hp:
            return

        screen_x, screen_y = to_screen(self.x, self.y, camera)
        x = screen_x - ENEMY_HP_BAR_WIDTH // 2
        y = screen_y - ENEMY_HP_BAR_OFFSET
        fill_width = int(ENEMY_HP_BAR_WIDTH * max(0, self.hp) / self.max_hp)
        pygame.draw.rect(
            screen,
            ENEMY_HP_BAR_BG,
            (x, y, ENEMY_HP_BAR_WIDTH, ENEMY_HP_BAR_HEIGHT),
        )
        pygame.draw.rect(
            screen,
            ENEMY_HP_BAR_FILL,
            (x, y, fill_width, ENEMY_HP_BAR_HEIGHT),
        )
