import sys

import pygame
from settings import *
from player import Player


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet vs Dead")

clock = pygame.time.Clock()

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self, target):
        self.x = target.x - WIDTH // 2
        self.y = target.y - HEIGHT // 2

player = Player()
camera = Camera()

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    player.update(camera)
    camera.update(player)

    screen.fill((20, 20, 20))

    player.draw(screen, camera)

    pygame.display.flip()
