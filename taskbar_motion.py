import math
import random


class TaskbarMotion:
    """Coordinates are Qt logical pixels, so mixed-DPI screens stay consistent."""
    def __init__(self):
        self.target = None
        self.x = None
        self.speed = 0.0
        self.phase = 0.0
        self.running = False
        self.rng = random.Random()

    def reset(self):
        self.target = self.x = None
        self.speed = 0.0

    def step(self, x, left, right, dt, fox):
        if self.target is None:
            self.x = float(x)
            candidates = [max(left, x - self.rng.randint(180, 480)),
                          min(right, x + self.rng.randint(180, 480))]
            self.target = max(candidates, key=lambda p: abs(p - x))
            self.running = self.rng.random() < (.65 if fox else .4)
        self.target = max(left, min(right, self.target))
        distance = self.target - self.x
        direction = 1 if distance >= 0 else -1
        max_speed = (130 if fox else 105) if self.running else (58 if fox else 45)
        desired = min(max_speed, math.sqrt(2 * 180 * abs(distance)))
        self.speed = min(desired, self.speed + 180 * dt)
        step = min(abs(distance), self.speed * dt)
        self.x += direction * step
        self.phase = (self.phase + step / (8 if self.running else 6)) % 8
        arrived = abs(self.target - self.x) < .5
        return round(self.x), direction, arrived


def floor_y(area, foot_offset=134):
    return area.bottom() + 1 - foot_offset
