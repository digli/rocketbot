import math
import time
import emergency
from constants import *
from utils import vec3, output


class StrategyManager:
    def __init__(self, agent):
        self.agent = agent
        self.options = [
            GoForScore(agent),
            # GoForSave(agent),
            GoForBoost(agent),
            GoToGoal(agent),
            IdleInPlace(agent),
            RunParallelWithBall(agent),
            # LandSafely(agent),
            Retreat(agent)
        ]
        self.strategy = self.options[0]
        self.emergency_strategy = None
        # self.emergency_strategy = emergency.KickOff(agent)

    def update(self):
        # Highest priority: Emergency Strategy
        self.check_emergency_strategy()
        if self.emergency_strategy is not None:
            # No emergency present, continue with normal strats
            optimal_strategy = self.find_optimal_strategy()
            if optimal_strategy != self.strategy:
                self.strategy = optimal_strategy
                print('{}\tchanged strat to {}'.format(self.agent.player, self.strategy))

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

    def get_output(self):
        return output()

    def score(self):
        return 0


class GoForBoost(Strategy):
    def get_output(self):
        if self.target is None:
            return GoForScore(self.agent).get_output()
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
        angle = self.player.angle_to(self.target.position)
        points = 1
        points -= dist / 150
        points -= self.player.boost / 100
        points -= abs(angle) / math.pi
        return points


class GoForScore(Strategy):
    def get_output(self):
        intersect = self.player.intersection_point(self.ball)
        # EXPERIMENTAL STUFF
        desired_impact = vec3()
        desired_angle = self.ball.desired_angle_to_goal(self.opponent.goal_coords)
        desired_impact.x = intersect.x + BALL_RADIUS * math.sin(desired_angle)
        desired_impact.z = intersect.z + BALL_RADIUS * math.cos(desired_angle)
        angle = self.player.angle_to(desired_impact)
        # /EXPERIMENTAL STUFF
        if (self.player.should_dodge_to(desired_impact)):
            return self.agent.dodge(desired_impact)
        speed = 1
        # if not self.ball.reachable_from_ground():
        #     intersect = self.ball.next_bounce_position()
        #     time_to_intersect = self.ball.next_bounce
        #     distance = (self.player.position - intersect).length()
        #     if self.player.speed / distance > time_to_intersect:
        #         speed = -1
                # somehow. maybe return output here?
                # or should this be refactored into another strategy
        # angle = self.player.angle_to(intersect)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        boost = (self.player.position - intersect).length_squared() > 50**2
        boost |= self.ball.reachable_from_ground()
        boost &= self.player.should_boost() and not powerslide
        boost &= speed == 1
        speed *= not powerslide
        return output(yaw=turn, speed=speed, boost=boost, powerslide=powerslide)

    def score(self):
        points = 1 + self.player.boost / 100 + self.player.speed / 100
        distance_to_ball = (self.player.position - self.ball.position).length()
        points -= distance_to_ball / 150
        points -= abs(self.player.angle_to(self.ball)) / math.pi
        return points


class GoForSave(Strategy):
    # Ignored for now, dont know why bot gets stuck in this strategy
    def get_output(self):
        intersect = self.player.intersection_point(self.ball)
        angle = self.player.angle_to(intersect)
        turn = angle * YAW_SENSITIVITY
        boost = self.player.should_boost()
        return output(yaw=turn, boost=boost)

    def score(self):
        # Gets fucking stuck here and i dont know why
        return int(self.ball.going_into_goal(self.player))


class GoToGoal(Strategy):
    def get_output(self):
        if self.player.should_dodge_to(self.player.goal_coords):
            return self.agent.dodge(self.player.goal_coords)
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
        # needs work
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
            self.ball.going_into_goal(self.player)):
            return int(self.player.speed < self.ball.ground_speed)
        return 0 # TODO


class IdleInPlace(Strategy):
    def get_output(self):
        return output(speed=0)

    def score(self):
        return 0


class LandSafely(Strategy):
    def get_output(self):
        pitch = self.player.pitch * -1 * YAW_SENSITIVITY
        roll = 0 # TODO, player.rotation.up.y ? or rotation.right probably
        powerslide = abs(roll) > 0.2
        return output(yaw=roll, pitch=pitch, powerslide=powerslide)

    def score(self):
        # check if player.up and player.pitch is correct
        # is_airbound needs improvement before we put this strat in action
        return int(self.player.velocity.y < -1 and self.player.is_airbound())


class AttemptAerial(Strategy):
    pass

