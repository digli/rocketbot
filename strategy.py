import math
import time
import emergency
from constants import *
from utils import vec3, output


class StrategyManager:
    def __init__(self, agent):
        self.agent = agent
        self.options = [
            # Score(agent),
            # HitBall(agent),
            GoForScore(agent)
            # TurnAround(agent),
            # GrabBoost(agent),
            # DodgeIntoBall(agent),
            # ChaseBall(agent)
            # GoForSave(agent),
            # GoToGoal(agent),
            # IdleInPlace(agent),
            # RunParallelWithBall(agent),
            # LandSafely(agent),
            # Retreat(agent)
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


class MockPrediction(Strategy):
    # TODO
    def get_output(self):
        return output()

    def score(self):
        return 0


class ChaseBall(Strategy):
    def get_output(self):
        desired_ball_direction = self.opponent.goal_coords - self.ball.position
        desired_impact_direction = desired_ball_direction - self.ball.velocity
        required_impact_angle = desired_impact_direction.ground_direction() + math.pi
        intersect = self.ball.position.clone()
        intersect.x += BALL_RADIUS * math.sin(required_impact_angle)
        intersect.z += BALL_RADIUS * math.cos(required_impact_angle)

        angle = self.player.angle_to(intersect)
        # if self.player.should_dodge_to(self.ball.position):
        #     return self.agent.dodge(self.ball)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        boost = not powerslide and self.player.should_boost()
        return output(yaw=turn, speed=1, boost=boost, powerslide=powerslide)

    def score(self):
        return -self.player.time_to_ball

class GrabBoost(Strategy):
    def get_output(self):
        target = self.player.optimal_boost
        angle = self.player.angle_to(target.position)
        if self.player.should_dodge_to(target.position):
            return self.agent.dodge(target.position)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        boost = not powerslide and self.player.should_boost()
        return output(yaw=turn, speed=1, boost=boost, powerslide=powerslide)

    def score(self):
        # TODO: write this function
        return self.agent.boost_tracker.optimal_boost_score()
        ##########
        self.target = self.player.optimal_boost
        if self.target is None:
            # No available boosts
            return 0
        distance = (self.player.position - self.target.position).length()
        points = 1
        points -= distance / 150
        points -= self.player.boost / 100
        points -= abs(self.player.angle_to(self.target.position)) / math.pi
        return points


class DodgeIntoBall(Strategy):
    # Helper to trigger emergency without doing it in other strategies
    def get_output(self):
        return self.agent.dodge(self.ball.position)

    def score(self):
        if self.player.will_hit_ball:
            return 1.5 - self.player.time_to_ball
        return 0


class HitBall(Strategy):
    def get_output(self):
        angle = self.player.angle_to(self.ball)
        turn = angle * YAW_SENSITIVITY
        boost = self.player.desired_ball_impact_speed - 1 > self.player.speed
        return output(yaw=turn, boost=boost)

    def score(self):
        return 10 / (self.player.position - self.ball.position).length_squared()

class Score(Strategy):
    def get_output(self):
        if (self.player.should_dodge_to_position(self.player.ball_intersection_point)):
            return self.agent.dodge(self.player.ball_intersection_point)
        angle = self.player.angle_to(self.player.ball_intersection_point)
        turn = angle * YAW_SENSITIVITY
        # acc = int(self.player.desired_ball_impact_speed + 1 < self.player.speed)
        powerslide = self.player.should_powerslide(angle)
        boost = self.player.desired_ball_impact_speed - 1 > self.player.speed
        boost &= not powerslide
        return output(yaw=turn, speed=1, boost=boost, powerslide=powerslide)

    def score(self):
        # hmmmmmmm
        close_enough = self.player.time_to_ball - self.opponent.time_to_ball > -0.5
        angle = self.player.angle_to(self.player.ball_intersection_point)
        points = 1
        # points -= max(abs(angle) - POWERSLIDE_THRESHOLD, 0)
        return points

        points = 1 + self.player.boost / 100 + self.player.speed / 100
        distance_to_ball = (self.player.position - self.ball.position).length()
        points -= distance_to_ball / 150
        points -= abs(self.player.angle_to(self.ball)) / math.pi
        return points



class TurnAround(Strategy):
    def get_output(self):
        speed = 0 if self.player.speed > 20 else 1
        return output(yaw=1, speed=speed, powerslide=True) 

    def score(self):
        if self.player.time_to_ball < 0 and abs(self.player.angle_to(self.ball)) > 2:
            return 3
        return 0

class GoForScore(Strategy):
    # this strategy has way too much resposibility, refactor into smaller strats
    def get_output(self):
        intersect = self.player.ball_intersection_point
        # EXPERIMENTAL STUFF
        desired_impact = self.player.ball_intersection_point
        # desired_angle = self.ball.desired_angle_to_goal(self.opponent.goal_coords)
        # desired_impact.x = intersect.x + BALL_RADIUS * math.sin(desired_angle) * 0.6
        # desired_impact.z = intersect.z + BALL_RADIUS * math.cos(desired_angle) * 0.6
        angle = self.player.angle_to(desired_impact)
        # /EXPERIMENTAL STUFF
        if (self.player.should_dodge_to(desired_impact)):
            return self.agent.dodge(desired_impact)
        if self.player.should_dodge_to(self.ball):
            return self.agent.dodge(self.ball.position)
        speed = 1
        if not self.ball.reachable_from_ground():
            intersect = self.ball.next_bounce_position
            time_to_intersect = self.ball.next_bounce
            distance = (self.player.position - intersect).length()
            if self.player.speed / distance > time_to_intersect:
                speed = -1
                # somehow. maybe return output here?
                # or should this be refactored into another strategy
        # angle = self.player.angle_to(intersect)
        turn = angle * YAW_SENSITIVITY
        powerslide = self.player.should_powerslide(angle)
        boost = (self.player.position - intersect).length_squared() > 50**2
        boost |= self.ball.reachable_from_ground()
        boost &= self.player.should_boost() and not powerslide
        boost &= speed == 1
        return output(yaw=turn, speed=speed, boost=boost, powerslide=powerslide)

    def score(self):
        if self.player.time_to_ball < 0 or not self.player.will_hit_ball:
            return 0
        points = 1 + max(self.player.boost / 100, self.player.speed / 100)
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
        angle = self.player.angle_to(self.target)
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
        powerslide = abs(self.player.rotation.right.z) > 0.2
        roll = int(powerslide)
        return output(yaw=roll, pitch=pitch, powerslide=powerslide)

    def score(self):
        # check if player.up and player.pitch is correct
        # is_airbound needs improvement before we put this strat in action
        return int(self.player.velocity.y < -1 and self.player.is_airbound())


class AttemptAerial(Strategy):
    pass



class BumpEnemy(Strategy):
    def score(self):
        if not self.ball.going_into_goal(self.opponent):
            return 0
        # Determine if we can intercept opponents direction to ball
        # Predict opponents turn arc, check his boost
        return 0
