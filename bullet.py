import math

from entity import draw_rotated_sprite, load_sprite
from settings import (
    BULLET_DAMAGE,
    BULLET_MAX_DISTANCE,
    BULLET_MOVE_STEPS,
    BULLET_RADIUS,
    BULLET_SPRITE,
    BULLET_SPRITE_SIZE,
    BULLET_SPEED,
)
from utils import distance


class Bullet:
    _sprite = None

    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.start_x = self.x
        self.start_y = self.y
        self.angle = angle
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.alive = True
        if Bullet._sprite is None:
            Bullet._sprite = load_sprite(BULLET_SPRITE, BULLET_SPRITE_SIZE)

    def update(self, game_map, enemies):
        if not self.alive:
            return

        for _ in range(BULLET_MOVE_STEPS):
            next_x = self.x + self.vx / BULLET_MOVE_STEPS
            next_y = self.y + self.vy / BULLET_MOVE_STEPS

            for enemy in enemies:
                if enemy.is_alive and enemy.hits_circle(next_x, next_y, BULLET_RADIUS):
                    enemy.take_damage(BULLET_DAMAGE)
                    self.alive = False
                    return

            if game_map.circle_hits_wall(next_x, next_y, BULLET_RADIUS):
                self.alive = False
                return

            self.x = next_x
            self.y = next_y

        if distance(self.start_x, self.start_y, self.x, self.y) >= BULLET_MAX_DISTANCE:
            self.alive = False

    def draw(self, screen, camera):
        if not self.alive:
            return
        draw_rotated_sprite(screen, Bullet._sprite, self.x, self.y, camera, self.angle)
