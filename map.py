import math

import pygame

from settings import (
    BOARD_HITS,
    BOARD_INTERACT_DISTANCE,
    BOARD_SEGMENT_SIZE,
    COLOR_FLOOR,
    COLOR_WALL,
    COLOR_WINDOW,
    COLOR_WINDOW_BOARDED,
    MAP_HEIGHT,
    MAP_WIDTH,
    WALL_THICKNESS,
    WINDOW_WIDTH,
    ENEMY_RADIUS,
    ZOMBIE_BOARD_ATTACK_COOLDOWN,
)

DOOR_WIDTH = 110


class Window:
    """Проём в стене. Доски: по BOARD_HITS ударов на каждую."""

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
        return len(self.boards) > 0

    @property
    def is_fully_boarded(self):
        return len(self.boards) >= self.max_boards

    def blocks_movement(self, for_enemy=False):
        if for_enemy:
            return self.has_boards
        return True

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
        return math.hypot(x - cx, y - cy)

    @property
    def is_open(self):
        return True

    def _board_color(self, hp):
        ratio = hp / BOARD_HITS
        base = COLOR_WINDOW_BOARDED
        return (
            int(base[0] * ratio + 60 * (1 - ratio)),
            int(base[1] * ratio + 40 * (1 - ratio)),
            int(base[2] * ratio + 30 * (1 - ratio)),
        )

    def draw(self, screen, camera):
        screen_rect = self.rect.move(-camera.x, -camera.y)
        pygame.draw.rect(screen, COLOR_WINDOW, screen_rect)

        if not self.boards:
            return

        horizontal = self.rect.width >= self.rect.height
        max_b = self.max_boards

        if horizontal:
            seg_w = screen_rect.width / max_b
            for i, hp in enumerate(self.boards):
                seg = pygame.Rect(
                    screen_rect.x + int(i * seg_w) + 1,
                    screen_rect.y + 1,
                    int(seg_w) - 2,
                    screen_rect.height - 2,
                )
                pygame.draw.rect(screen, self._board_color(hp), seg)
        else:
            seg_h = screen_rect.height / max_b
            for i, hp in enumerate(self.boards):
                seg = pygame.Rect(
                    screen_rect.x + 1,
                    screen_rect.y + int(i * seg_h) + 1,
                    screen_rect.width - 2,
                    int(seg_h) - 2,
                )
                pygame.draw.rect(screen, self._board_color(hp), seg)

    def spawn_outside(self, offset):
        cx = self.rect.centerx
        cy = self.rect.centery
        if self.side == "top":
            return cx, self.rect.top - offset
        if self.side == "bottom":
            return cx, self.rect.bottom + offset
        if self.side == "left":
            return self.rect.left - offset, cy
        return self.rect.right + offset, cy


class GameMap:
    """Прямоугольное здание с комнатами внутри."""

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

    def _floor(self, x, y, w, h, alt=False):
        if w > 0 and h > 0:
            self.floor_rects.append((pygame.Rect(x, y, w, h), alt))

    def _window_h(self, x_center, y, side):
        self.windows.append(
            Window(
                pygame.Rect(
                    x_center - WINDOW_WIDTH // 2,
                    y,
                    WINDOW_WIDTH,
                    WALL_THICKNESS,
                ),
                side,
            )
        )

    def _window_v(self, x, y_center, side):
        self.windows.append(
            Window(
                pygame.Rect(
                    x,
                    y_center - WINDOW_WIDTH // 2,
                    WALL_THICKNESS,
                    WINDOW_WIDTH,
                ),
                side,
            )
        )

    def _horizontal_wall(self, x1, x2, y, windows=(), gaps=(), side="top"):
        openings = [(c, "window") for c in windows] + [(c, "door") for c in gaps]
        openings.sort(key=lambda item: item[0])

        cursor = x1
        for center, kind in openings:
            half = WINDOW_WIDTH // 2 if kind == "window" else DOOR_WIDTH // 2
            gap_start = center - half
            gap_end = center + half
            if gap_start > cursor:
                self._wall(cursor, y, gap_start - cursor, WALL_THICKNESS)
            if kind == "window":
                self._window_h(center, y, side)
            cursor = gap_end
        if cursor < x2:
            self._wall(cursor, y, x2 - cursor, WALL_THICKNESS)

    def _vertical_wall(self, y1, y2, x, windows=(), gaps=(), side="left"):
        openings = [(c, "window") for c in windows] + [(c, "door") for c in gaps]
        openings.sort(key=lambda item: item[0])

        cursor = y1
        for center, kind in openings:
            half = WINDOW_WIDTH // 2 if kind == "window" else DOOR_WIDTH // 2
            gap_start = center - half
            gap_end = center + half
            if gap_start > cursor:
                self._wall(x, cursor, WALL_THICKNESS, gap_start - cursor)
            if kind == "window":
                self._window_v(x, center, side)
            cursor = gap_end
        if cursor < y2:
            self._wall(x, cursor, WALL_THICKNESS, y2 - cursor)

    def _build_layout(self):
        t = WALL_THICKNESS

        ox, oy = 120, 100
        build_w, build_h = 1640, 1000
        bx2 = ox + build_w
        by2 = oy + build_h

        split_x = ox + build_w // 2
        split_y = oy + build_h // 3

        # --- Пол: один ровный прямоугольник + оттенки комнат поверх ---
        inner_w = build_w - 2 * t
        inner_h = build_h - 2 * t
        self._floor(ox + t, oy + t, inner_w, inner_h, alt=False)
        self._floor(ox + t, oy + t, inner_w, split_y - oy - t, alt=False)
        self._floor(ox + t, split_y, split_x - ox - t, by2 - split_y - t, alt=True)
        self._floor(split_x + t, split_y, bx2 - split_x - 2 * t, by2 - split_y - t, alt=False)

        # --- Внешний контур (прямоугольник) ---
        self._corner(ox, oy)
        self._corner(bx2 - t, oy)
        self._corner(ox, by2 - t)
        self._corner(bx2 - t, by2 - t)

        self._horizontal_wall(ox + t, bx2 - t, oy, [520, 1120], side="top")
        self._horizontal_wall(ox + t, bx2 - t, by2 - t, [820], side="bottom")
        self._vertical_wall(oy + t, by2 - t, ox, [300, 700], side="left")
        self._vertical_wall(oy + t, by2 - t, bx2 - t, [620], side="right")

        # --- Внутренние перегородки ---
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
    def _push_circle_out_of_rect(x, y, radius, rect):
        closest_x = max(rect.left, min(x, rect.right))
        closest_y = max(rect.top, min(y, rect.bottom))
        dx = x - closest_x
        dy = y - closest_y
        dist_sq = dx * dx + dy * dy
        if dist_sq >= radius * radius:
            return x, y
        dist = math.sqrt(dist_sq) if dist_sq else 0.001
        overlap = radius - dist
        return x + dx / dist * overlap, y + dy / dist * overlap

    def resolve_circle_move(self, x, y, radius, dx, dy, for_enemy=False):
        rects = self.collision_rects(for_enemy=for_enemy)
        x += dx
        for rect in rects:
            x, y = self._push_circle_out_of_rect(x, y, radius, rect)
        y += dy
        for rect in rects:
            x, y = self._push_circle_out_of_rect(x, y, radius, rect)
        return x, y

    def circle_hits_wall(self, x, y, radius):
        for rect in self.walls:
            closest_x = max(rect.left, min(x, rect.right))
            closest_y = max(rect.top, min(y, rect.bottom))
            dx = x - closest_x
            dy = y - closest_y
            if dx * dx + dy * dy < radius * radius:
                return True
        for window in self.windows:
            if window.has_boards or window.blocks_movement(for_enemy=False):
                rect = window.rect
                closest_x = max(rect.left, min(x, rect.right))
                closest_y = max(rect.top, min(y, rect.bottom))
                dx = x - closest_x
                dy = y - closest_y
                if dx * dx + dy * dy < radius * radius:
                    return True
        return False

    @staticmethod
    def segment_hits_circle(x1, y1, x2, y2, cx, cy, radius):
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return math.hypot(x1 - cx, y1 - cy) < radius

        t = max(0.0, min(1.0, ((cx - x1) * dx + (cy - y1) * dy) / length_sq))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        return math.hypot(closest_x - cx, closest_y - cy) < radius

    def clamp_camera(self, cam_x, cam_y, view_w, view_h):
        min_x = -view_w * 0.2
        min_y = -view_h * 0.2
        max_x = self.width - view_w * 0.8
        max_y = self.height - view_h * 0.8
        return max(min_x, min(cam_x, max_x)), max(min_y, min(cam_y, max_y))

    def get_spawn_points_outside(self, offset):
        points = []
        for window in self.windows:
            if window.is_open:
                points.append(window.spawn_outside(offset))
        return points

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
        if window is None:
            return False
        return window.add_board()

    def process_zombie_board_attacks(self, enemies, dt):
        for window in self.windows:
            if window._attack_cooldown > 0:
                window._attack_cooldown = max(0.0, window._attack_cooldown - dt)

        for enemy in enemies:
            if not enemy.is_alive:
                continue
            for window in self.windows:
                if not window.has_boards:
                    continue
                if window._attack_cooldown > 0:
                    continue
                if window.distance_to(enemy.x, enemy.y) > ENEMY_RADIUS + 25:
                    continue
                window.damage_board(1)
                window._attack_cooldown = ZOMBIE_BOARD_ATTACK_COOLDOWN
                break

    def draw(self, screen, camera):
        for floor_rect, alt in self.floor_rects:
            color = COLOR_FLOOR
            pygame.draw.rect(screen, color, floor_rect.move(-camera.x, -camera.y))

        for wall in self.walls:
            pygame.draw.rect(screen, COLOR_WALL, wall.move(-camera.x, -camera.y))

        for window in self.windows:
            window.draw(screen, camera)
