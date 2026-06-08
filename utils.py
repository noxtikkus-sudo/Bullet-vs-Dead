import math


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def circles_overlap(x1, y1, r1, x2, y2, r2):
    return distance(x1, y1, x2, y2) <= r1 + r2


def to_screen(x, y, camera):
    return int(x - camera.x), int(y - camera.y)


def normalize_move(dx, dy, speed):
    dist = math.hypot(dx, dy)
    if dist == 0:
        return 0.0, 0.0
    step = min(speed, dist)
    return dx / dist * step, dy / dist * step


def tick_down(timer, dt):
    return max(0.0, timer - dt) if timer > 0 else 0.0


def clamp(value, low, high):
    return max(low, min(value, high))
