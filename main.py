import math

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


STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Bullet vs Dead")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, HUD_FONT_SIZE)
        self.title_font = pygame.font.SysFont(None, 76)
        self.menu_font = pygame.font.SysFont(None, 42)
        self.small_font = pygame.font.SysFont(None, 26)
        self.running = True
        self.state = STATE_MENU
        self.menu_index = 0

        self.game_map = None
        self.navgrid = None
        self.pathfinder = None
        self.player = None
        self.camera = None
        self.wave_manager = None
        self.bullets = []

    def _start_new_game(self):
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
        self.state = STATE_PLAYING
        self.menu_index = 0

    @property
    def _can_continue(self):
        return self.player is not None and self.player.alive

    def _menu_items(self):
        if self.state == STATE_PAUSED:
            return [
                ("Продолжить", "continue", True),
                ("Новая игра", "new_game", True),
                ("В главное меню", "main_menu", True),
                ("Выход", "quit", True),
            ]

        if self.state == STATE_GAME_OVER:
            return [
                ("Новая игра", "new_game", True),
                ("В главное меню", "main_menu", True),
                ("Выход", "quit", True),
            ]

        return [
            ("Новая игра", "new_game", True),
            ("Продолжить", "continue", self._can_continue),
            ("Выход", "quit", True),
        ]

    def _move_menu_selection(self, step):
        items = self._menu_items()
        if not items:
            return

        for _ in items:
            self.menu_index = (self.menu_index + step) % len(items)
            if items[self.menu_index][2]:
                return

    def _activate_menu_item(self):
        items = self._menu_items()
        if not items:
            return

        _, action, enabled = items[self.menu_index]
        if not enabled:
            return

        if action == "new_game":
            self._start_new_game()
        elif action == "continue":
            self.state = STATE_PLAYING
            self.menu_index = 0
        elif action == "main_menu":
            self.state = STATE_MENU
            self.menu_index = 0
        elif action == "quit":
            self.running = False

    def _handle_menu_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_w, pygame.K_UP):
            self._move_menu_selection(-1)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self._move_menu_selection(1)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate_menu_item()
        elif event.key == pygame.K_ESCAPE:
            if self.state == STATE_PAUSED and self._can_continue:
                self.state = STATE_PLAYING
            elif self.state == STATE_MENU:
                self.running = False

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state != STATE_PLAYING:
                self._handle_menu_event(event)
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED
                self.menu_index = 0
                continue

            if not self.player.alive:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                angle = math.atan2(
                    mouse_y + self.camera.y - self.player.y,
                    mouse_x + self.camera.x - self.player.x,
                )
                self.bullets.append(Bullet(self.player.x, self.player.y, angle))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.game_map.try_board_window(self.player.x, self.player.y)

    def _update(self, dt):
        if self.state != STATE_PLAYING:
            return
        if not self.player.alive:
            self.state = STATE_GAME_OVER
            self.menu_index = 0
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

        if not self.player.alive:
            self.state = STATE_GAME_OVER
            self.menu_index = 0
            return

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

    def _draw_game(self):
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

    def _draw_centered_text(self, text, font, y, color=COLOR_UI):
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=(WIDTH // 2, y)))

    def _draw_menu(self, title, subtitle=""):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        self._draw_centered_text(title, self.title_font, 150)
        if subtitle:
            self._draw_centered_text(subtitle, self.small_font, 205)

        items = self._menu_items()
        y = 285
        for index, (label, _, enabled) in enumerate(items):
            prefix = "> " if index == self.menu_index else "  "
            color = COLOR_UI if enabled else (120, 120, 120)
            self._draw_centered_text(f"{prefix}{label}", self.menu_font, y, color)
            y += 52

        self._draw_centered_text(
            "W/S или стрелки - выбор, Enter - подтвердить, Esc - назад",
            self.small_font,
            HEIGHT - 45,
        )

    def _draw(self):
        if self.game_map is not None:
            self._draw_game()
        else:
            self.screen.fill(COLOR_BG)

        if self.state == STATE_MENU:
            self._draw_menu("Bullet vs Dead", "Выживи против волн зомби")
        elif self.state == STATE_PAUSED:
            self._draw_menu("Пауза", "Игра остановлена")
        elif self.state == STATE_GAME_OVER:
            self._draw_menu("Game Over", "Зомби добрались до тебя")

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
