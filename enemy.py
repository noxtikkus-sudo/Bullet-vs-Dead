from entity import CircleEntity
from settings import (
    COLOR_ENEMY,
    ENEMY_HP,
    ENEMY_RADIUS,
    ENEMY_REPATH_TIME,
    ENEMY_SPEED,
    ENEMY_WAYPOINT_REACH,
)
from utils import distance, normalize_move


class Enemy(CircleEntity):
    def __init__(self, x, y, hp=None):
        super().__init__(x, y, ENEMY_RADIUS, ENEMY_HP if hp is None else hp)
        self.path = []
        self.path_index = 0
        self.repath_timer = 0.0

    def _move_toward(self, target_x, target_y, game_map):
        move_x, move_y = normalize_move(target_x - self.x, target_y - self.y, ENEMY_SPEED)
        if move_x == 0 and move_y == 0:
            return
        self.x, self.y = game_map.resolve_circle_move(
            self.x, self.y, self.radius, move_x, move_y, for_enemy=True
        )

    def update(self, player, game_map, dt, navgrid, pathfinder):
        if not self.alive:
            return

        self.repath_timer -= dt
        if self.repath_timer <= 0 or self.path_index >= len(self.path):
            start = navgrid.world_to_cell(self.x, self.y)
            goal = navgrid.world_to_cell(player.x, player.y)
            self.path = pathfinder.find_path(navgrid, start, goal)
            self.path_index = 1 if len(self.path) > 1 else 0
            self.repath_timer = ENEMY_REPATH_TIME

        if self.path and self.path_index < len(self.path):
            wx, wy = navgrid.cell_to_world(self.path[self.path_index])
            self._move_toward(wx, wy, game_map)
            if distance(self.x, self.y, wx, wy) < ENEMY_WAYPOINT_REACH:
                self.path_index += 1
        else:
            self._move_toward(player.x, player.y, game_map)

    def draw(self, screen, camera):
        self.draw_circle(screen, camera, COLOR_ENEMY)
