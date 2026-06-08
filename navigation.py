from settings import NAV_CELL_SIZE, NAV_OBSTACLE_PADDING, NAV_SEARCH_RADIUS

INF = 10**9


class NavGrid:
    def __init__(self, world_width, world_height):
        self.cell_size = NAV_CELL_SIZE
        self.cols = world_width // NAV_CELL_SIZE + 1
        self.rows = world_height // NAV_CELL_SIZE + 1
        self.blocked = [[False] * self.cols for _ in range(self.rows)]

    def world_to_cell(self, x, y):
        cx = int(x // self.cell_size)
        cy = int(y // self.cell_size)
        cx = max(0, min(cx, self.cols - 1))
        cy = max(0, min(cy, self.rows - 1))
        return cx, cy

    def cell_to_world(self, cell):
        cx, cy = cell
        half = self.cell_size / 2
        return cx * self.cell_size + half, cy * self.cell_size + half

    def is_walkable(self, cell):
        cx, cy = cell
        if cx < 0 or cy < 0 or cx >= self.cols or cy >= self.rows:
            return False
        return not self.blocked[cy][cx]

    def neighbors(self, cell):
        cx, cy = cell
        deltas = ((1, 0), (-1, 0), (0, 1), (0, -1))
        return [
            (cx + dx, cy + dy)
            for dx, dy in deltas
            if self.is_walkable((cx + dx, cy + dy))
        ]

    def closest_walkable(self, cell):
        if self.is_walkable(cell):
            return cell
        cx, cy = cell
        for r in range(1, NAV_SEARCH_RADIUS):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    cand = (cx + dx, cy + dy)
                    if self.is_walkable(cand):
                        return cand
        return None

    def rebuild_from_map(self, game_map):
        self.blocked = [[False] * self.cols for _ in range(self.rows)]
        padding = NAV_OBSTACLE_PADDING * 2
        for wall in game_map.walls:
            padded = wall.inflate(padding, padding)
            x1, y1 = self.world_to_cell(padded.left, padded.top)
            x2, y2 = self.world_to_cell(padded.right, padded.bottom)
            for cy in range(y1, y2 + 1):
                for cx in range(x1, x2 + 1):
                    self.blocked[cy][cx] = True


class AStarPathfinder:
    @staticmethod
    def _heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, navgrid, start, goal):
        start = navgrid.closest_walkable(start)
        goal = navgrid.closest_walkable(goal)
        if start is None or goal is None:
            return []

        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}

        while open_set:
            current = min(open_set, key=lambda c: f_score.get(c, INF))
            open_set.remove(current)

            if current == goal:
                return self._build_path(came_from, current)

            for neighbor in navgrid.neighbors(current):
                new_g = g_score[current] + 1
                if new_g >= g_score.get(neighbor, INF):
                    continue
                came_from[neighbor] = current
                g_score[neighbor] = new_g
                f_score[neighbor] = new_g + self._heuristic(neighbor, goal)
                open_set.add(neighbor)

        return []

    @staticmethod
    def _build_path(came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
