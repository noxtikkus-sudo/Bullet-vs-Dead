import pygame
from settings import BULLET_SPEED, BULLET_RADIUS
import math


class Bullet():
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

        # направление
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)


    def update(self):
        self.x += self.dx * BULLET_SPEED
        self.y += self.dy * BULLET_SPEED


    def draw(self, screen, camera):
        screen_x = self.x - camera.x
        screen_y = self.y - camera.y

        pygame.draw.circle(screen, (255, 255, 0),
                           (int(screen_x), int(screen_y)),
                           BULLET_RADIUS)




