import pygame
import math
from settings import PLAYER_SPEED


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0


    def update(self, camera):
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0

        if keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_s]:
            dy += PLAYER_SPEED
        if keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_d]:
            dx += PLAYER_SPEED

        self.x += dx * PLAYER_SPEED
        self.y += dy * PLAYER_SPEED

        mouse_x, mouse_y = pygame.mouse.get_pos()

        world_mouse_x = mouse_x + camera.x
        world_mouse_y = mouse_y + camera.y

        self.angle = math.atan2(world_mouse_y - self.y,
                                world_mouse_x - self.x)


    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y

        pygame.draw.circle(screen, (0, 255, 0),
                           (int(screen_x), int(screen_y)), 10)

        vision_x = screen_x + math.cos(self.angle) * 40
        vision_y = screen_y + math.sin(self.angle) * 40

        pygame.draw.line(screen, (0, 255, 255),
                         (screen_x, screen_y),
                         (vision_x, vision_y), 3)







