import time

class BigBoost:
    def __init__(self, z, x):
        self.z = z
        self.x = x
        self.taken_timestamp = 0

    @property
    def time_left(self):
        return time.time() - self.taken_timestamp

    @property
    def is_available(self):
        return self.time_left >= 10 # 10 seconds respawn time

    def pop(self):
        if self.is_available:
            self.taken_timestamp = time.time()

    def distance_squared(self, other):
        return (other.z - self.z) ** 2 + (other.x - self.x) ** 2

class BoostTracker:
    def __init__(self, player, opponent):
        self.boost_radius_squared = 30 # idk, test this number
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

    @property
    def closest_big_boost(self):
        closest = self.big_boosts[0]
        min_distance = 99999999 # arbitrary big number
        for b in self.big_boosts:
            distance = b.distance_squared(self.player.position)
            if distance < min_distance:
                closest = b
                min_distance = distance
        return closest

    def update(self):
        for b in self.big_boosts:
            if not b.is_available:
                continue
            if (b.distance_squared(self.player.position) < self.boost_radius_squared or 
                b.distance_squared(self.opponent.position) < self.boost_radius_squared):
                b.pop()


