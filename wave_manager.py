import math
import random

from enemy import Enemy
from settings import HEIGHT, WIDTH

WAVE_BASE_COUNT = 3
WAVE_COUNT_PER_LEVEL = 1
SPAWN_DISTANCE = 120


class WaveManager:
    """Spawns enemy waves around the player."""

    def __init__(self):
        self.wave = 0
        self.enemies = []

    def enemy_count_for_wave(self, wave_number):
        return WAVE_BASE_COUNT + (wave_number - 1) * WAVE_COUNT_PER_LEVEL

    def start_next_wave(self, player_x, player_y):
        self.wave += 1
        count = self.enemy_count_for_wave(self.wave)
        self.enemies = [
            Enemy(*self._spawn_position(player_x, player_y))
            for _ in range(count)
        ]

    def _spawn_position(self, player_x, player_y):
        angle = random.uniform(0, 2 * math.pi)
        distance = max(WIDTH, HEIGHT) // 2 + SPAWN_DISTANCE
        x = player_x + math.cos(angle) * distance
        y = player_y + math.sin(angle) * distance
        return x, y

    def update(self, player):
        for enemy in self.enemies:
            enemy.update(player)

    def all_defeated(self):
        return bool(self.enemies) and all(
            not enemy.is_alive for enemy in self.enemies
        )
