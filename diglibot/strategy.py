import math
import functools
from utils import vec3

class Controls:
    MAX = 32767
    MIN = 0
    MIDDLE = 16383
    LEFT = MIN
    RIGHT = MAX
    # Values might be wrong
    NOSE_UP = MAX
    NOSE_DOWN = MIN

def output_vector(yaw, pitch=Controls.MIDDLE, speed=1, jump=0, boost=0, powerslide=0):
    acceleration = 0
    retardation = 0
    if speed > 0:
        acceleration = int(round(speed * Controls.MAX))
    elif speed < 0:
        retardation = int(round(abs(speed) * Controls.MAX))
    return [yaw, pitch, acceleration, retardation, jump, boost, powerslide]

def angle_diff(a1, a2):
    return math.atan2(math.sin(a1-a2), math.cos(a1-a2))

def correct_yaw(car, target):
    angle_to_target = math.atan2(target.x - car.position.x, target.z - car.position.z)
    diff = angle_diff(car.forward, angle_to_target)
    correction = int(Controls.MIDDLE + Controls.MIDDLE * diff * 7)
    correction = min(max(correction, Controls.MIN), Controls.MAX)
    powerslide = int(abs(diff) > 1.8)
    return (correction, powerslide)


class StrategyManager:
    def __init__(self, player, opponent, ball, boost_tracker):
        args = (player, opponent, ball, boost_tracker)
        self.options = [
            GoForScore(*args),
            GoForSave(*args),
            GoForBoost(*args),
            GoToGoal(*args),
            IdleInPlace(*args),
            Retreat(*args)
        ]
        # Chase ball at game start
        self.strategy = self.options[0]

    def update(self):
        optimal_strategy = self.find_optimal_strategy()
        if optimal_strategy != self.strategy:
            self.strategy = optimal_strategy
            self.strategy.on_change()

    def get_output_vector(self):
        return self.strategy.get_output_vector()

    def find_optimal_strategy(self):
        return max(self.options, key=lambda a: a.score())
        # gt = lambda a, b: return a.score() > b.score()
        # return functools.reduce(lambda a, b: a if gt(a, b) else b, self.options)


class Strategy:
    def __init__(self, player, opponent, ball, boost_tracker):
        self.player = player
        self.opponent = opponent
        self.ball = ball
        self.boost_tracker = boost_tracker

    def __str__(self):
        return self.__class__.__name__

    def on_change(self):
        print('{0.player!s} changed strat to {0!s}'.format(self))
        print('{!s} has {} boost'.format(self.player, self.player.boost))
        self.initiate_strategy()

    # Override following functions
    def initiate_strategy(self):
        pass

    def get_output_vector(self):
        return output_vector(Controls.MIDDLE)

    def score(self):
        return 0


class GoForBoost(Strategy):
    def initiate_strategy(self):
        print('Closest big boost: {!s}'.format(self.target.position))

    def get_output_vector(self):
        if not self.target.is_available():
            self.target = self.boost_tracker.closest_big_boost()
            # if self.target is None: CHANGE STRAT
            print('Boost taken. New target: {!s}'.format(self.target.position))
        (turn, powerslide) = correct_yaw(self.player, self.target.position)
        # boosting while powersliding is redundant
        boost = 1 ^ powerslide
        return output_vector(turn, speed=1, boost=boost, powerslide=powerslide)

    def score(self):
        self.target = self.boost_tracker.closest_big_boost()
        if self.target is None:
            # No available boosts
            return 0
        dist = (self.player.position - self.target.position).length()
        points = 1
        points -= dist / 150
        points -= self.player.boost / 100
        return points


class GoForSave(Strategy):

    def score(self):
        return 0
        # todo ...
        if ball.going_into_goal(self.player.goal_coords.z):
            return 1


class IdleInPlace(Strategy):
    def get_output_vector(self):
        (turn, powerslide) = correct_yaw(self.player, self.ball.position)
        return output_vector(turn, speed=0, powerslide=powerslide)

    def score(self):
        # TODO
        return 0


class GoForScore(Strategy):
    # GROUND BALL CHASING ONLY
    # Jumping and dodging occurs in AttemptAerial
    def get_output_vector(self):
        # TODO: take velocity of ball into accord, calculating point of contact
        # Determine if we should use boost
        (turn, powerslide) = correct_yaw(self.player, self.ball.position)
        boost = int(self.ball.reachable_from_ground()) if not powerslide else 0
        return output_vector(turn, boost=boost, powerslide=powerslide)

    def score(self):
        # needs a lot of work
        points = 1 + self.player.boost / 100
        distance_to_ball = (self.player.position - self.ball.position).length()
        points -= distance_to_ball / 150
        return points


class GoToGoal(Strategy):
    def get_output_vector(self):
        (turn, powerslide) = correct_yaw(self.player, self.player.goal_coords)
        boost = int(self.car.speed < 40)
        return output_vector(turn, boost=boost, powerslide=powerslide)

    def score(self):
        # TODO
        return 0


class Retreat(Strategy):
    # Should we avoid hitting ball?
    # Or should that be covered by GoForSave strategy
    def get_output_vector(self):
        self.target = self.player.clone()
        # magic number 0.9 to stop car from running up the wall
        self.target.z = self.goal_coords.z * 0.9
        (turn, powerslide) = correct_yaw(self.player, target)
        return output_vector(turn, powerslide=powerslide)

    def score(self):
        if abs(self.goal_coords.z) - abs(self.player.z) < 20:
            return 0
        if (self.player.position - self.ball.position).length_squared() > \
            (self.opponent.position - self.ball.position).length_squared():
            # return some variable score
            return 0.5
        # Check if closer to ball
        # Check if car to ball angle results in own goal
        return 0

class AttemptAerial(Strategy):
    pass
