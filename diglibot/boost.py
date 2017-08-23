import time
import functools

class BigBoost:
    def __init__(self, x, z):
        self.x = x
        self.z = z
        self.taken_timestamp = 0
        self.radius_squared = 10 # idk, test this number

    def time_left(self):
        return time.time() - self.taken_timestamp

    def is_available(self):
        return self.time_left() >= 10 # 10 seconds respawn time

    def pop(self):
        if self.is_available():
            print('BigBoost({0.x},{0.z}) popped'.format(self))
            self.taken_timestamp = time.time()

    def distance_squared(self, other):
        return (other.z - self.z) ** 2 + (other.x - self.x) ** 2

    def in_range(self, other):
        return self.distance_squared(other) < self.radius_squared

class BoostTracker:
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.big_boosts = [
            # Might need to take a closer look at boost coordinates
            BigBoost(73, 0),
            BigBoost(-73, 0),
            BigBoost(64, 81),
            BigBoost(-64, 81),
            BigBoost(-64, -81),
            BigBoost(64, -81)
        ]

    def closest_big_boost(self):
        pos = self.player.position
        gt = lambda a, b: return a.distance_squared(pos) > b.distance_squared(pos)
        return functools.reduce(lambda a, b: a if gt(a, b) else b, self.big_boosts)

    def update(self):
        for b in self.big_boosts:
            if (b.in_range(self.player.position) or 
                b.in_range(self.opponent.position)):
                b.pop()


