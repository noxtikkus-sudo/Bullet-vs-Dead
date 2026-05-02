import pygame

from bullet import Bullet
from player import Player
from settings import COLOR_BG, FPS, HEIGHT, WIDTH

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
bullets = []

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            bullets.append(Bullet(player.x, player.y, player.angle))

    if not running:
        break

    player.update(camera)
    camera.update(player)

    for bullet in bullets:
        bullet.update()

    screen.fill(COLOR_BG)

    player.draw(screen, camera)
    for bullet in bullets:
        bullet.draw(screen, camera)

    pygame.display.flip()

pygame.quit()