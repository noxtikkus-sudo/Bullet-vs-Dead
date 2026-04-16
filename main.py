import pygame
from settings import *
from player import Player


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet vs Dead")

clock = pygame.time.Clock()

player = Player(WIDTH, HEIGHT)

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
