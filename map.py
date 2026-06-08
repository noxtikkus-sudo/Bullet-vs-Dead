import math

import pygame

from settings import (
    BOARD_DRAW_INSET,
    BOARD_DRAW_MARGIN,
    BOARD_HITS,
    BOARD_INTERACT_DISTANCE,
    BOARD_SEGMENT_SIZE,
    COLOR_FLOOR,
    COLOR_WALL,
    COLOR_WINDOW,
    COLOR_WINDOW_BOARDED,
    DOOR_WIDTH,
    ENEMY_RADIUS,
    MAP_HEIGHT,
    MAP_WIDTH,
    WALL_THICKNESS,
    WINDOW_WIDTH,
    ZOMBIE_BOARD_ATTACK_COOLDOWN,
    ZOMBIE_BOARD_ATTACK_RANGE,
)
from utils import distance, tick_down


class Window:
    def __init__(self, rect, side):
        self.rect = pygame.Rect(rect)
        self.side = side
        self.boards = []
        self._attack_cooldown = 0.0

    @property
    def max_boards(self):
        length = max(self.rect.width, self.rect.height)
        return max(1, length // BOARD_SEGMENT_SIZE)

    @property
    def has_boards(self):
        return bool(self.boards)

    @property
    def is_fully_boarded(self):
        return len(self.boards) >= self.max_boards

    def blocks_movement(self, for_enemy=False):
        return self.has_boards if for_enemy else True

    def add_board(self):
        if self.is_fully_boarded:
            return False
        self.boards.append(BOARD_HITS)
        return True

    def damage_board(self, amount=1):
        if not self.boards:
            return
        self.boards[0] -= amount
        if self.boards[0] <= 0:
            self.boards.pop(0)

    def distance_to(self, x, y):
        cx = max(self.rect.left, min(x, self.rect.right))
        cy = max(self.rect.top, min(y, self.rect.bottom))
        return distance(x, y, cx, cy)

    def draw(self, screen, camera):
        screen_rect = self.rect.move(-camera.x, -camera.y)
        pygame.draw.rect(screen, COLOR_WINDOW, screen_rect)
        if not self.boards:
            return

        horizontal = self.rect.width >= self.rect.height
        segment_count = self.max_boards
        segment_length = (
            screen_rect.width / segment_count
            if horizontal
            else screen_rect.height / segment_count
        )

        for i in range(len(self.boards)):
            if horizontal:
                seg = pygame.Rect(
                    screen_rect.x + int(i * segment_length) + BOARD_DRAW_MARGIN,
                    screen_rect.y + BOARD_DRAW_MARGIN,
                    int(segment_length) - BOARD_DRAW_INSET,
                    screen_rect.height - BOARD_DRAW_INSET,
                )
            else:
                seg = pygame.Rect(
                    screen_rect.x + BOARD_DRAW_MARGIN,
                    screen_rect.y + int(i * segment_length) + BOARD_DRAW_MARGIN,
                    screen_rect.width - BOARD_DRAW_INSET,
                    int(segment_length) - BOARD_DRAW_INSET,
                )
            pygame.draw.rect(screen, COLOR_WINDOW_BOARDED, seg)

    def spawn_outside(self, offset):
        offsets = {
            "top": (self.rect.centerx, self.rect.top - offset),
            "bottom": (self.rect.centerx, self.rect.bottom + offset),
            "left": (self.rect.left - offset, self.rect.centery),
            "right": (self.rect.right + offset, self.rect.centery),
        }
        return offsets[self.side]


class GameMap:
    def __init__(self):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.walls = []
        self.windows = []
        self.floor_rects = []
        self.spawn_point = (0.0, 0.0)
        self._build_layout()

    def _wall(self, x, y, w, h):
        if w > 0 and h > 0:
            self.walls.append(pygame.Rect(x, y, w, h))

    def _corner(self, x, y):
        self._wall(x, y, WALL_THICKNESS, WALL_THICKNESS)

    def _floor(self, x, y, w, h):
        if w > 0 and h > 0:
            self.floor_rects.append(pygame.Rect(x, y, w, h))

    def _add_window(self, rect, side):
        self.windows.append(Window(rect, side))

    def _window_h(self, x_center, y, side):
        self._add_window(
            pygame.Rect(x_center - WINDOW_WIDTH // 2, y, WINDOW_WIDTH, WALL_THICKNESS),
            side,
        )

    def _window_v(self, x, y_center, side):
        self._add_window(
            pygame.Rect(x, y_center - WINDOW_WIDTH // 2, WALL_THICKNESS, WINDOW_WIDTH),
            side,
        )

    def _wall_with_openings(self, start, end, fixed, windows, gaps, horizontal, side):
        openings = [(c, WINDOW_WIDTH // 2, "window") for c in windows]
        openings += [(c, DOOR_WIDTH // 2, "door") for c in gaps]
        openings.sort(key=lambda item: item[0])

        cursor = start
        for center, half, kind in openings:
            gap_start = center - half
            gap_end = center + half
            if gap_start > cursor:
                if horizontal:
                    self._wall(cursor, fixed, gap_start - cursor, WALL_THICKNESS)
                else:
                    self._wall(fixed, cursor, WALL_THICKNESS, gap_start - cursor)
            if kind == "window":
                if horizontal:
                    self._window_h(center, fixed, side)
                else:
                    self._window_v(fixed, center, side)
            cursor = gap_end

        if cursor < end:
            if horizontal:
                self._wall(cursor, fixed, end - cursor, WALL_THICKNESS)
            else:
                self._wall(fixed, cursor, WALL_THICKNESS, end - cursor)

    def _horizontal_wall(self, x1, x2, y, windows=(), gaps=(), side="top"):
        self._wall_with_openings(x1, x2, y, windows, gaps, horizontal=True, side=side)

    def _vertical_wall(self, y1, y2, x, windows=(), gaps=(), side="left"):
        self._wall_with_openings(y1, y2, x, windows, gaps, horizontal=False, side=side)

    def _build_layout(self):
        t = WALL_THICKNESS
        ox, oy = 120, 100
        build_w, build_h = 1640, 1000
        bx2 = ox + build_w
        by2 = oy + build_h
        split_x = ox + build_w // 2
        split_y = oy + build_h // 3

        inner_w = build_w - 2 * t
        inner_h = build_h - 2 * t
        self._floor(ox + t, oy + t, inner_w, inner_h)
        self._floor(ox + t, oy + t, inner_w, split_y - oy - t)
        self._floor(ox + t, split_y, split_x - ox - t, by2 - split_y - t)
        self._floor(split_x + t, split_y, bx2 - split_x - 2 * t, by2 - split_y - t)

        self._corner(ox, oy)
        self._corner(bx2 - t, oy)
        self._corner(ox, by2 - t)
        self._corner(bx2 - t, by2 - t)

        self._horizontal_wall(ox + t, bx2 - t, oy, windows=[520, 1120], side="top")
        self._horizontal_wall(ox + t, bx2 - t, by2 - t, windows=[820], side="bottom")
        self._vertical_wall(oy + t, by2 - t, ox, windows=[300, 700], side="left")
        self._vertical_wall(oy + t, by2 - t, bx2 - t, windows=[620], side="right")

        self._corner(split_x - t, split_y - t)
        self._vertical_wall(split_y, by2 - t, split_x, gaps=[split_y + 220])
        self._horizontal_wall(ox + t, split_x, split_y, gaps=[ox + 320])
        self._horizontal_wall(split_x + t, bx2 - t, oy + 420, gaps=[split_x + 220])

        self.spawn_point = (ox + build_w // 2, oy + build_h // 2)

    def collision_rects(self, for_enemy=False):
        rects = list(self.walls)
        for window in self.windows:
            if window.blocks_movement(for_enemy=for_enemy):
                rects.append(window.rect)
        return rects

    @staticmethod
    def _circle_hits_rect(x, y, radius, rect):
        closest_x = max(rect.left, min(x, rect.right))
        closest_y = max(rect.top, min(y, rect.bottom))
        dx = x - closest_x
        dy = y - closest_y
        return dx * dx + dy * dy < radius * radius

    def _push_out(self, x, y, radius, rect):
        closest_x = max(rect.left, min(x, rect.right))
        closest_y = max(rect.top, min(y, rect.bottom))
        dx = x - closest_x
        dy = y - closest_y
        dist = math.hypot(dx, dy)
        if dist >= radius:
            return x, y
        if dist == 0:
            return x + radius, y
        push = (radius - dist) / dist
        return x + dx * push, y + dy * push

    def resolve_circle_move(self, x, y, radius, dx, dy, for_enemy=False):
        rects = self.collision_rects(for_enemy=for_enemy)
        x += dx
        for rect in rects:
            x, y = self._push_out(x, y, radius, rect)
        y += dy
        for rect in rects:
            x, y = self._push_out(x, y, radius, rect)
        return x, y

    def circle_hits_wall(self, x, y, radius):
        rects = self.walls + [window.rect for window in self.windows]
        return any(self._circle_hits_rect(x, y, radius, rect) for rect in rects)

    def get_spawn_points_outside(self, offset):
        return [window.spawn_outside(offset) for window in self.windows]

    def get_window_near(self, x, y, max_dist=BOARD_INTERACT_DISTANCE):
        best = None
        best_dist = max_dist
        for window in self.windows:
            if window.is_fully_boarded:
                continue
            dist = window.distance_to(x, y)
            if dist < best_dist:
                best_dist = dist
                best = window
        return best

    def try_board_window(self, x, y):
        window = self.get_window_near(x, y)
        return window.add_board() if window else False

    def process_zombie_board_attacks(self, enemies, dt):
        for window in self.windows:
            window._attack_cooldown = tick_down(window._attack_cooldown, dt)

        attack_range = ENEMY_RADIUS + ZOMBIE_BOARD_ATTACK_RANGE
        for enemy in enemies:
            if not enemy.is_alive:
                continue
            for window in self.windows:
                if not window.has_boards or window._attack_cooldown > 0:
                    continue
                if window.distance_to(enemy.x, enemy.y) > attack_range:
                    continue
                window.damage_board(1)
                window._attack_cooldown = ZOMBIE_BOARD_ATTACK_COOLDOWN
                break

    def draw(self, screen, camera):
        offset = (-camera.x, -camera.y)
        for floor_rect in self.floor_rects:
            pygame.draw.rect(screen, COLOR_FLOOR, floor_rect.move(offset))
        for wall in self.walls:
            pygame.draw.rect(screen, COLOR_WALL, wall.move(offset))
        for window in self.windows:
            window.draw(screen, camera)
