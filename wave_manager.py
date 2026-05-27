import math
import random

from enemy import Enemy
from settings import SPAWN_DISTANCE, WAVE_BASE_COUNT, WAVE_COUNT_PER_LEVEL


class WaveManager:
    def __init__(self, game_map=None):
        self.game_map = game_map
        self.wave = 0
        self.enemies = []

    def enemy_count_for_wave(self, wave_number):
        return WAVE_BASE_COUNT + (wave_number - 1) * WAVE_COUNT_PER_LEVEL

    def start_next_wave(self, player_x, player_y):
        self.wave += 1
        count = self.enemy_count_for_wave(self.wave)
        self.enemies = []
        for i in range(count):
            x, y = self._spawn_position(player_x, player_y)
            spread = 45
            angle = (2 * math.pi / max(count, 1)) * i
            x += math.cos(angle) * spread
            y += math.sin(angle) * spread
            self.enemies.append(Enemy(x, y))

    def _spawn_position(self, player_x, player_y):
        if self.game_map is not None:
            points = self.game_map.get_spawn_points_outside(SPAWN_DISTANCE)
            if points:
                return random.choice(points)

        angle = random.uniform(0, 2 * math.pi)
        distance = SPAWN_DISTANCE + 200
        x = player_x + math.cos(angle) * distance
        y = player_y + math.sin(angle) * distance
        return x, y

    def update(self, player, game_map=None):
        collision_map = game_map if game_map is not None else self.game_map
        for enemy in self.enemies:
            enemy.update(player, collision_map)

    def remove_dead(self):
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive]

    def wave_cleared(self):
        """Все враги мертвы (вызывать до remove_dead)."""
        return bool(self.enemies) and all(not enemy.is_alive for enemy in self.enemies)
