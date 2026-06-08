import pygame

from bullet import Bullet
from camera import Camera
from collision import check_enemy_player_collisions, cleanup_alive
from map import GameMap
from navigation import AStarPathfinder, NavGrid
from player import Player
from settings import (
    BOARD_HITS,
    COLOR_BG,
    COLOR_UI,
    FPS,
    HEIGHT,
    HUD_FONT_SIZE,
    HUD_HINT_Y,
    HUD_HP_Y,
    HUD_WAVE_Y,
    HUD_X,
    MAP_HEIGHT,
    MAP_WIDTH,
    WIDTH,
)
from wave_manager import WaveManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Bullet vs Dead")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, HUD_FONT_SIZE)
        self.running = True

        self.game_map = GameMap()
        self.navgrid = NavGrid(MAP_WIDTH, MAP_HEIGHT)
        self.pathfinder = AStarPathfinder()
        self.navgrid.rebuild_from_map(self.game_map)

        self.player = Player()
        self.player.x, self.player.y = self.game_map.spawn_point
        self.camera = Camera()
        self.wave_manager = WaveManager(self.game_map)
        self.bullets = []
        self.wave_manager.start_next_wave(self.player.x, self.player.y)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if not self.player.alive:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.bullets.append(Bullet(self.player.x, self.player.y, self.player.angle))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.game_map.try_board_window(self.player.x, self.player.y)

    def _update(self, dt):
        if not self.player.alive:
            return

        self.player.update(self.camera, dt, self.game_map)
        self.camera.update(self.player, self.game_map)
        self.wave_manager.update(
            self.player, self.game_map, dt, self.navgrid, self.pathfinder
        )
        self.game_map.process_zombie_board_attacks(self.wave_manager.enemies, dt)

        for bullet in self.bullets:
            bullet.update(self.game_map, self.wave_manager.enemies)

        check_enemy_player_collisions(self.wave_manager.enemies, self.player)
        cleanup_alive(self.bullets)

        if self.wave_manager.wave_cleared():
            self.wave_manager.start_next_wave(self.player.x, self.player.y)
        else:
            self.wave_manager.remove_dead()

    def _draw_hud(self, hint=""):
        self.screen.blit(
            self.font.render(f"HP: {self.player.hp}", True, COLOR_UI),
            (HUD_X, HUD_HP_Y),
        )
        self.screen.blit(
            self.font.render(f"Wave: {self.wave_manager.wave}", True, COLOR_UI),
            (HUD_X, HUD_WAVE_Y),
        )
        if hint:
            self.screen.blit(
                self.font.render(hint, True, COLOR_UI),
                (HUD_X, HUD_HINT_Y),
            )

    def _draw(self):
        self.screen.fill(COLOR_BG)
        self.game_map.draw(self.screen, self.camera)

        for enemy in self.wave_manager.enemies:
            enemy.draw(self.screen, self.camera)
        if self.player.alive:
            self.player.draw(self.screen, self.camera)
        for bullet in self.bullets:
            bullet.draw(self.screen, self.camera)

        hint = ""
        if self.player.alive and self.game_map.get_window_near(self.player.x, self.player.y):
            hint = f"E — поставить доску ({BOARD_HITS} удара на доску)"
        self._draw_hud(hint)

        if not self.player.alive:
            text = self.font.render("Game Over — закрой окно", True, COLOR_UI)
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
