import math

import pygame

from settings import (
    COLOR_PLAYER,
    COLOR_PLAYER_AIM,
    PLAYER_DAMAGE_COOLDOWN,
    PLAYER_MAX_HP,
    PLAYER_SPEED,
)

PLAYER_RADIUS = 10
AIM_LINE_LENGTH = 40


class Player:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.hp = PLAYER_MAX_HP
        self.alive = True
        self._damage_cooldown = 0.0

    def take_damage(self, amount):
        if not self.alive or self._damage_cooldown > 0:
            return
        self.hp -= amount
        self._damage_cooldown = PLAYER_DAMAGE_COOLDOWN
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(self, camera, dt, game_map=None):
        if self._damage_cooldown > 0:
            self._damage_cooldown = max(0.0, self._damage_cooldown - dt)

        if not self.alive:
            return

        keys = pygame.key.get_pressed()

        dx = 0.0
        dy = 0.0
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1

        length = math.hypot(dx, dy)
        if length:
            scale = PLAYER_SPEED / length
            dx *= scale
            dy *= scale

        if game_map is not None:
            self.x, self.y = game_map.resolve_circle_move(
                self.x, self.y, PLAYER_RADIUS, dx, dy, for_enemy=False
            )
        else:
            self.x += dx
            self.y += dy

        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + camera.x
        world_mouse_y = mouse_y + camera.y
        self.angle = math.atan2(world_mouse_y - self.y, world_mouse_x - self.x)

    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y

        pygame.draw.circle(
            screen,
            COLOR_PLAYER,
            (int(screen_x), int(screen_y)),
            PLAYER_RADIUS,
        )

        vision_x = screen_x + math.cos(self.angle) * AIM_LINE_LENGTH
        vision_y = screen_y + math.sin(self.angle) * AIM_LINE_LENGTH

        pygame.draw.line(
            screen,
            COLOR_PLAYER_AIM,
            (screen_x, screen_y),
            (vision_x, vision_y),
            3,
        )
