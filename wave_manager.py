import random

from enemy import Enemy
from settings import SPAWN_DISTANCE, WAVE_BASE_COUNT, WAVE_COUNT_PER_LEVEL


class WaveManager:
    def __init__(self, game_map):
        self.game_map = game_map
        self.wave = 0
        self.enemies = []

    def start_next_wave(self, player_x, player_y):
        self.wave += 1
        count = WAVE_BASE_COUNT + (self.wave - 1) * WAVE_COUNT_PER_LEVEL
        self.enemies = [
            Enemy(*self._spawn_position(player_x, player_y))
            for _ in range(count)
        ]

    def _spawn_position(self, player_x, player_y):
        points = self.game_map.get_spawn_points_outside(SPAWN_DISTANCE)
        if points:
            return random.choice(points)
        return player_x + SPAWN_DISTANCE, player_y

    def update(self, player, game_map, dt, navgrid, pathfinder):
        for enemy in self.enemies:
            enemy.update(player, game_map, dt, navgrid, pathfinder)

    def remove_dead(self):
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive]

    def wave_cleared(self):
        return self.enemies and all(not enemy.is_alive for enemy in self.enemies)
