import math
import time
from constants import *
from emergency import *
from utils import vec3, output


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
        self.emergency_strategy = KickOff(agent, agent.ball.position)

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

    def get_output(self):
        if self.emergency_strategy is not None:
            return self.emergency_strategy.get_output()
        return self.strategy.get_output()

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
        self.initiate_strategy()

    # Override following functions
    def initiate_strategy(self):
        pass

    def get_output(self):
        return output()

    def score(self):
        return 0


class GoForBoost(Strategy):
    def get_output(self):
        if not self.target.is_available():
            self.target = self.boost_tracker.closest_big_boost()
            # target cannot be None here, boost cant be popped between score()
            # and this function.
        angle = self.player.angle_to(self.target.position)
        if (self.player.should_dodge_to(self.target.position) 
            and abs(angle) < 0.5):
            dodge_strategy = DodgeTowards(self.agent, self.target.position)
            self.agent.trigger_emergency(dodge_strategy)
            return dodge_strategy.get_output()
        turn = angle * YAW_SENSITIVITY
        powerslide = self.car.should_powerslide(angle)
        # boosting while powersliding is redundant
        boost = not powerslide and self.player.below_max_speed()
        return output(yaw=turn, speed=1, boost=boost, powerslide=powerslide)

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


class GoForScore(Strategy):
    # GROUND BALL CHASING ONLY
    # Jumping and dodging occurs in AttemptAerial
    def get_output(self):
        # TODO: take velocity of ball into accord, calculating point of contact
        # Determine if we should use boost
        angle = self.player.angle_to(self.ball.position)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        boost = self.player.below_max_speed() and self.ball.reachable_from_ground()
        boost = boost and not powerslide
        return output(yaw=turn, boost=boost, powerslide=powerslide)

    def score(self):
        # needs a lot of work
        points = 1 + self.player.boost / 100
        distance_to_ball = (self.player.position - self.ball.position).length()
        points -= distance_to_ball / 150
        return points


class GoToGoal(Strategy):
    def get_output(self):
        angle = self.player.angle_to(self.player.goal_coords)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        boost = self.player.below_max_speed()
        return output(yaw=turn, boost=boost, powerslide=powerslide)

    def score(self):
        # TODO
        return 0


class Retreat(Strategy):
    # Should we avoid hitting ball?
    # Or should that be covered by GoForSave strategy
    def get_output(self):
        self.target = self.player.position.clone()
        # magic number 0.9 to stop car from running up the wall
        self.target.z = self.player.goal_coords.z * 0.9
        angle = self.player.angle_to(self.target.position)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        return output(yaw=turn, powerslide=powerslide)

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


class GoForSave(Strategy):
    def score(self):
        return 0
        # todo ...
        if ball.going_into_goal(self.player.goal_coords.z):
            return 1


class IdleInPlace(Strategy):
    def get_output(self):
        return output(speed=0)

    def score(self):
        return 0

class AttemptAerial(Strategy):
    pass

