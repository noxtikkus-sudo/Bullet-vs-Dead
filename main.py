import pygame

from bullet import Bullet
from collision import (
    check_enemy_player_collisions,
    cleanup_bullets,
)
from map import GameMap
from player import Player
from settings import COLOR_BG, COLOR_UI, FPS, HEIGHT, WIDTH
from wave_manager import WaveManager

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bullet vs Dead")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self, target, game_map):
        self.x = target.x - WIDTH // 2
        self.y = target.y - HEIGHT // 2
        self.x, self.y = game_map.clamp_camera(self.x, self.y, WIDTH, HEIGHT)


def draw_hud(surface, player, wave):
    hp_text = font.render(f"HP: {player.hp}", True, COLOR_UI)
    wave_text = font.render(f"Wave: {wave}", True, COLOR_UI)
    surface.blit(hp_text, (10, 10))
    surface.blit(wave_text, (10, 40))


def draw_game_over(surface):
    text = font.render("Game Over — закрой окно", True, COLOR_UI)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    surface.blit(text, rect)


game_map = GameMap()
player = Player()
player.x, player.y = game_map.spawn_point

camera = Camera()
wave_manager = WaveManager(game_map)
bullets = []

wave_manager.start_next_wave(player.x, player.y)

running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if (
            player.alive
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            bullets.append(Bullet(player.x, player.y, player.angle))

    if not running:
        break

    if player.alive:
        player.update(camera, dt, game_map)
        camera.update(player, game_map)

        wave_manager.update(player, game_map)

        for bullet in bullets:
            bullet.update(game_map, wave_manager.enemies)

        check_enemy_player_collisions(wave_manager.enemies, player)
        cleanup_bullets(bullets)

        if wave_manager.wave_cleared():
            wave_manager.start_next_wave(player.x, player.y)
        else:
            wave_manager.remove_dead()

    screen.fill(COLOR_BG)
    game_map.draw(screen, camera)

    for enemy in wave_manager.enemies:
        enemy.draw(screen, camera)

    if player.alive:
        player.draw(screen, camera)

    for bullet in bullets:
        bullet.draw(screen, camera)

    draw_hud(screen, player, wave_manager.wave)
    if not player.alive:
        draw_game_over(screen)

    pygame.display.flip()

pygame.quit()
