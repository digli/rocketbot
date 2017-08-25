import time
from constants import *
from utils import vec3

class BigBoost:
    def __init__(self, x, z):
        self.position = vec3(x=x, z=z)
        self.taken_timestamp = 0

    def __str__(self):
        return 'BigBoost({}, {})'.format(self.position.x, self.position.z)

    def seconds_since_pop(self):
        return time.time() - self.taken_timestamp

    def is_available(self):
        return self.seconds_since_pop() >= BIG_BOOST_RESPAWN_TIME

    def pop(self):
        if self.is_available():
            self.taken_timestamp = time.time()

    def distance_squared(self, other):
        return (other - self.position).length_squared()

    def in_range_of(self, other):
        return self.distance_squared(other) < BOOST_RADIUS_SQUARED

class BoostTracker:
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent
        self.big_boosts = [
            BigBoost(BOOST_MIDFIELD_X, 0),
            BigBoost(-BOOST_MIDFIELD_X, 0),
            BigBoost(BOOST_CORNER_X, BOOST_CORNER_Z),
            BigBoost(-BOOST_CORNER_X, BOOST_CORNER_Z),
            BigBoost(-BOOST_CORNER_X, -BOOST_CORNER_Z),
            BigBoost(BOOST_CORNER_X, -BOOST_CORNER_Z)
        ]

    def closest_big_boost(self):
        pos = self.player.position
        available = [b for b in self.big_boosts if b.is_available()]
        if len(available) == 0:
            return None
        return min(available, key=lambda b: b.distance_squared(pos))

    def update(self):
        for b in self.big_boosts:
            if (b.in_range_of(self.player.position) or 
                b.in_range_of(self.opponent.position)):
                b.pop()
