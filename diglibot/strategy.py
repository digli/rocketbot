import math
import time
from constants import *
from utils import vec3, angle, output
from emergency import *


def correct_yaw(car, target):
    diff = angle.car_to_target(car, target)
    correction = int(STICK_MIDDLE + STICK_MIDDLE * diff * YAW_SENSITIVITY)
    correction = min(max(correction, STICK_MIN), STICK_MAX)
    powerslide = abs(diff) > POWERSLIDE_THRESHOLD # TODO: try different values here
    return (correction, powerslide)


class StrategyManager:
    def __init__(self, agent):
        self.options = [
            GoForScore(agent),
            GoForSave(agent),
            GoForBoost(agent),
            GoToGoal(agent),
            IdleInPlace(agent),
            Retreat(agent)
        ]
        # Chase ball at game start
        self.strategy = self.options[0]
        self.emergency_strategy = DodgeTowards(agent, agent.ball.position)

    def update(self):
        # Highest priority: Emergency Strategy
        self.check_emergency_strategy()
        if self.emergency_strategy is not None:
            return None
        # No emergency present, continue with normal strats
        optimal_strategy = self.find_optimal_strategy()
        if optimal_strategy != self.strategy:
            self.strategy = optimal_strategy
            self.strategy.on_change()

    def check_emergency_strategy(self):
        if self.emergency_strategy is not None and self.emergency_strategy.is_finished():
            self.emergency_strategy = self.emergency_strategy.suggest_next_strategy()

    def get_output_vector(self):
        if self.emergency_strategy is not None:
            return self.emergency_strategy.get_output_vector()
        return self.strategy.get_output_vector()

    def find_optimal_strategy(self):
        return max(self.options, key=lambda a: a.score())



class Strategy:
    def __init__(self, agent):
        self.agent = agent
        self.player = agent.player
        self.opponent = agent.opponent
        self.ball = agent.ball
        self.boost_tracker = agent.boost_tracker

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
        return output.generate()

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
        dist_to_boost = (self.player.position - self.target.position).length()
        if (self.player.boost < 5 and self.player.on_ground() and dist_to_boost > 40):
            # Should probably take car speed into account when checking dist_to_boost
            # check if we're on ground? might get stuck in weird jumping patterns lol
            # TODO: TESTING, could be shit
            dodge_strategy = DodgeTowards(self.agent, self.target.position)
            self.agent.trigger_emergency(dodge_strategy)
            return dodge_strategy.get_output_vector()
        # boosting while powersliding is redundant
        boost = not powerslide
        return output.generate(yaw=turn, speed=1, boost=boost, powerslide=powerslide)

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
        return output.generate(yaw=turn, speed=0, powerslide=powerslide)

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
        boost = self.player.below_max_speed() and self.ball.reachable_from_ground() 
        boost = boost and not powerslide
        return output.generate(yaw=turn, boost=boost, powerslide=powerslide)

    def score(self):
        # needs a lot of work
        points = 1 + self.player.boost / 100
        distance_to_ball = (self.player.position - self.ball.position).length()
        points -= distance_to_ball / 150
        return points


class GoToGoal(Strategy):
    def get_output_vector(self):
        (turn, powerslide) = correct_yaw(self.player, self.player.goal_coords)
        boost = self.car.speed < 40
        return output.generate(yaw=turn, boost=boost, powerslide=powerslide)

    def score(self):
        # TODO
        return 0


class Retreat(Strategy):
    # Should we avoid hitting ball?
    # Or should that be covered by GoForSave strategy
    def get_output_vector(self):
        self.target = self.player.position.clone()
        # magic number 0.9 to stop car from running up the wall
        self.target.z = self.player.goal_coords.z * 0.9
        (turn, powerslide) = correct_yaw(self.player, target)
        return output.generate(yaw=turn, powerslide=powerslide)

    def score(self):
        return 0
        if abs(self.player.goal_coords.z) - abs(self.player.position.z) < 20:
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
