import math
import random

from enemy import Enemy
from settings import ENEMY_RADIUS, SPAWN_DISTANCE, WAVE_BASE_COUNT, WAVE_COUNT_PER_LEVEL
from utils import distance


class WaveManager:
    def __init__(self, game_map):
        self.game_map = game_map
        self.wave = 0
        self.enemies = []

    def start_next_wave(self, player_x, player_y):
        self.wave += 1
        count = WAVE_BASE_COUNT + (self.wave - 1) * WAVE_COUNT_PER_LEVEL
        self.enemies = []
        for _ in range(count):
            x, y = self._spawn_position(player_x, player_y, self.enemies)
            self.enemies.append(Enemy(x, y))

    def _spawn_position(self, player_x, player_y, existing_enemies):
        points = self.game_map.get_spawn_points_outside(SPAWN_DISTANCE)
        if not points:
            points = [(player_x + SPAWN_DISTANCE, player_y)]

        random.shuffle(points)
        min_distance = ENEMY_RADIUS * 2 + 8
        for point in points:
            if self._is_spawn_free(point, existing_enemies, min_distance):
                return point

        base_x, base_y = random.choice(points)
        for _ in range(24):
            angle = random.uniform(0, math.tau)
            offset = random.uniform(min_distance, min_distance * 3)
            point = (
                base_x + math.cos(angle) * offset,
                base_y + math.sin(angle) * offset,
            )
            if self._is_spawn_free(point, existing_enemies, min_distance):
                return point

        return base_x, base_y

    @staticmethod
    def _is_spawn_free(point, enemies, min_distance):
        x, y = point
        return all(distance(x, y, enemy.x, enemy.y) >= min_distance for enemy in enemies)

    def update(self, player, game_map, dt, navgrid, pathfinder):
        for enemy in self.enemies:
            enemy.update(player, game_map, dt, navgrid, pathfinder)

    def remove_dead(self):
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive]

    def wave_cleared(self):
        return self.enemies and all(not enemy.is_alive for enemy in self.enemies)
