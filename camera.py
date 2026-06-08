from settings import HEIGHT, WIDTH
from utils import clamp


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, target, game_map):
        self.x = target.x - WIDTH // 2
        self.y = target.y - HEIGHT // 2
        self.x = clamp(self.x, 0, max(0, game_map.width - WIDTH))
        self.y = clamp(self.y, 0, max(0, game_map.height - HEIGHT))
