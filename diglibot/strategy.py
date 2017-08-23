import math

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
    correction = int(Controls.MIDDLE + Controls.MIDDLE * diff * 5)
    correction = min(max(correction, Controls.MIN), Controls.MAX)
    powerslide = 1 if abs(diff) > 2.0 else 0
    return (correction, powerslide)

class StrategyManager:
    def __init__(self, player, opponent, ball, boost_tracker):
        args = (player, opponent, ball, boost_tracker)
        self.options = [
            GoForScore(*args),
            GoForSave(*args),
            GoForBoost(*args),
            GoToGoal(*args),
            IdleInPlace(*args)
        ]
        # Chase ball at game start
        self.strategy = self.options[0]

    def update(self):
        prev_strat = self.strategy
        self.strategy = self.find_optimal_strategy()
        if prev_strat != self.strategy:
            team = self.strategy.player.__class__.__name__
            print('{} car changed strat to {}'.format(team, self.strategy.name))

    def get_output_vector(self):
        return self.strategy.get_output_vector()

    def find_optimal_strategy(self):
        max_score = 0
        strategy = self.options[0]
        for s in self.options:
            score = s.score()
            if score > max_score:
                strategy = s
                max_score = score
        return strategy


class Strategy:
    def __init__(self, player, opponent, ball, boost_tracker):
        self.player = player
        self.opponent = opponent
        self.ball = ball
        self.boost_tracker = boost_tracker

    def get_output_vector(self):
        return output_vector(Controls.MIDDLE)

    def score(self):
        return 0

    @property
    def name(self):
        return self.__class__.__name__

class GoForBoost(Strategy):
    def get_output_vector(self):
        self.target = self.boost_tracker.closest_big_boost
        (turn, powerslide) = correct_yaw(self.player, self.target)
        return output_vector(turn, boost=1, powerslide=powerslide)

    def score(self):
        # maybe 0.2 - boost? (with a maximum of 0.8)
        return 0.5 - round(self.player.boost / 100)

class GoForSave(Strategy):
    pass


class IdleInPlace(Strategy):
    def get_output_vector(self):
        turn = correct_yaw(self.player, self.ball.position)
        return output_vector(turn, speed=0)

    def score(self):
        return 0


class GoForScore(Strategy):
    # GROUND BALL CHASING ONLY
    # Jumping and dodging occurs in AttemptAerial
    def get_output_vector(self):
        # TODO: take velocity of ball into accord, calculating point of contact
        # Determine if we should use boost
        (turn, powerslide) = correct_yaw(self.player, self.ball.position)
        boost = 1 if self.ball.reachable_from_ground() else 0
        boost = 0 if powerslide else boost 
        return output_vector(turn, boost=boost, powerslide=powerslide)

    def score(self):
        points = 1 + self.player.boost / 100
        distance_to_ball = (self.player.position - self.ball.position).length()
        points -= distance_to_ball / 150
        return points

class GoToGoal(Strategy):
    def get_output_vector(self):
        turn = correct_yaw(self.player, self.player.goal_coords)
        # boost or no boost?
        return output_vector(turn)

    def score(self):
        # TODO
        return 0


class AttemptAerial(Strategy):
    pass
