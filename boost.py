import time
from constants import *
from utils import vec3

class Boost:
    def __init__(self, x, z):
        self.position = vec3(x=x, z=z)
        self.taken_timestamp = 0

    def __str__(self):
        return '{0}({1.x}, {1.z})'.format(self.__class__.__name__, self.position)

    def seconds_since_pop(self):
        return time.time() - self.taken_timestamp

    def is_available(self):
        return self.seconds_since_pop() >= self.boost_respawn_time

    def pop(self):
        if self.is_available():
            self.taken_timestamp = time.time()

    def in_range_of(self, other):
        return (self.position - other).length_squared() < self.boost_radius_squared


class SmallBoost(Boost):
    def __init__(self, x, z):
        super().__init__(x, z)
        self.boost_respawn_time = SMALL_BOOST_RESPAWN_TIME
        self.boost_radius_squared = SMALL_BOOST_RADIUS_SQUARED


class BigBoost(Boost):
    def __init__(self, x, z):
        super().__init__(x, z)
        self.boost_respawn_time = BIG_BOOST_RESPAWN_TIME
        self.boost_radius_squared = BIG_BOOST_RADIUS_SQUARED


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

    def big_boost_score(self, boost, player):
        distance_squared = (boost.position - player.position).length_squared()
        angle = abs(player.angle_to(boost))
        return distance_squared * angle

    def find_optimal_boost(self):
        # hypothetical stuff
        available = [b for b in self.big_boosts if b.is_available()]
        if len(available) == 0:
            return None
        return min(available, key=lambda b: self.big_boost_score(b, self.player))

    def closest_big_boost(self):
        available = [b for b in self.big_boosts if b.is_available()]
        if len(available) == 0:
            return None
        distance = lambda boost: (boost.position - self.player.position).length_squared()
        return min(available, key=distance)

    def update(self):
        for b in self.big_boosts:
            if (b.in_range_of(self.player.position) or 
                b.in_range_of(self.opponent.position)):
                b.pop()
