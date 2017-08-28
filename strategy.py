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
        self.strategy = self.options[0]
        self.emergency_strategy = None
        # self.emergency_strategy = KickOff(agent, agent.ball.position)

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
            if self.target is None:
                return output(speed=0)
        angle = self.player.angle_to(self.target.position)
        if self.player.should_dodge_to(self.target.position):
            return self.agent.dodge(self.target.position)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        # boosting while powersliding is redundant
        boost = not powerslide and self.player.should_boost()
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
    def get_output(self):
        # TODO: take velocity of ball into accord, calculating point of contact
        # Determine if we should use boost
        if (self.player.should_dodge_to(self.ball) and 
            not self.agent.previous_output.powerslide):
            return self.agent.dodge(self.ball)
        intersect = self.player.intersection_point(self.ball)
        # EXPERIMENTAL STUFF
        desired_impact = vec3()
        desired_angle = self.ball.desired_angle_to_goal(self.opponent.goal_coords)
        desired_impact.x = intersect.x - BALL_RADIUS * math.sin(desired_angle)
        desired_impact.z = intersect.z - BALL_RADIUS * math.cos(desired_angle)
        angle = self.player.angle_to(desired_impact)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        boost = (self.player.position - intersect).length_squared() > 50**2
        boost |= self.ball.reachable_from_ground()
        boost &= self.player.should_boost() and not powerslide
        return output(yaw=turn, boost=boost, powerslide=powerslide)

    def score(self):
        # needs a lot of work
        points = 1 + self.player.boost / 100 + self.player.speed / 100
        distance_to_ball = (self.player.position - self.ball.position).length()
        points -= distance_to_ball / 150 + self.player.angle_to(self.ball) / math.pi
        return points


class GoToGoal(Strategy):
    def get_output(self):
        if self.player.should_dodge_to(self.target.position):
            return self.agent.dodge(self.target.position)
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
        if ((self.player.position - self.ball.position) > 
            (self.opponent.position - self.ball.position)):
            # return some variable score
            return 0.5
        # Check if closer to ball
        # Check if car to ball angle results in own goal
        return 0


class RunParallelWithBall(Strategy):
    def get_output(self):
        angle = self.player.forward - self.ball.ground_direction
        turn = angle * YAW_SENSITIVITY
        powerslide = abs(angle) > 2.2 # not as hard as usual
        boost = self.player.should_boost() and not powerslide
        return output(yaw=turn, boost=boost, powerslide=powerslide)

    def score(self):
        if (self.ball.ground_speed > CAR_MAX_SPEED and
            self.ball.going_into_goal(self.player.goal_coords.z)):
            return int(self.speed < self.ball.ground_speed) * 2
        return 0 # TODO


class GoForSave(Strategy):
    def get_output(self):
        intersect = self.player.intersection_point(self.ball)
        angle = self.player.angle_to(intersect)
        turn = angle * YAW_SENSITIVITY
        return output(yaw=turn, boost=self.player.should_boost())

    def score(self):
        if (self.ball.ground_speed < CAR_MAX_SPEED and 
            self.ball.going_into_goal(self.player.goal_coords.z)):
            return int(self.speed > self.ball.ground_speed) * 2
        return 0


class IdleInPlace(Strategy):
    def get_output(self):
        return output(speed=0)

    def score(self):
        return 0

class AttemptAerial(Strategy):
    pass

