import math

import pygame

from settings import (
    COLOR_PLAYER,
    COLOR_PLAYER_AIM,
    PLAYER_SPEED,
)

PLAYER_RADIUS = 10
AIM_LINE_LENGTH = 40


class Player:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0

    def update(self, camera):
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





