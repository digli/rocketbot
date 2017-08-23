import time
from utils import vec3

class BigBoost:
    def __init__(self, x, z):
        self.position = vec3(x=x, z=z)
        self.taken_timestamp = 0
        self.radius_squared = 16 # idk, test this number

    def seconds_since_pop(self):
        return time.time() - self.taken_timestamp

    def is_available(self):
        return self.seconds_since_pop() >= 10 # 10 seconds respawn time

    def pop(self):
        if self.is_available():
            print('BigBoost {!s} popped'.format(self.position))
            self.taken_timestamp = time.time()

    def distance_squared(self, other):
        return (other - self.position).length_squared()

    def in_range(self, other):
        return self.distance_squared(other) < self.radius_squared

class BoostTracker:
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.big_boosts = [
            # Might need to take a closer look at boost coordinates
            BigBoost(71, 0),
            BigBoost(-71, 0),
            BigBoost(62, 81),
            BigBoost(-62, 81),
            BigBoost(-62, -81),
            BigBoost(62, -81)
        ]

    def closest_big_boost(self):
        pos = self.player.position
        available = [b for b in self.big_boosts if b.is_available()]
        if len(available) == 0:
            return None
        return min(available, key=lambda b: b.distance_squared(pos))

    def update(self):
        for b in self.big_boosts:
            if (b.in_range(self.player.position) or 
                b.in_range(self.opponent.position)):
                b.pop()
