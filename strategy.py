
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
    return math.pi - abs(abs(a1 - a2) - math.pi)

def correction_yaw(a1, a2):
    angle = angle_diff(a1, a2)
    if (abs(angle) < 0.2):
        # 0.2 sweet spot? need to find proper deadzone
        return Controls.MIDDLE
    return Controls.LEFT if angle < 0 else Controls.RIGHT


class StrategyManager:
    def __init__(self, player, opponent, ball, boost_tracker):
        self.strats = [
            GoForBall(player, opponent, ball, boost_tracker),
            GoForBoost(player, opponent, ball, boost_tracker),
            GoToGoal(player, opponent, ball, boost_tracker)
        ]
        # Chase ball at game start
        self.strategy = self.strats[0]

    def update(self):
        prev_strat = self.strategy
        self.strategy = self.find_optimal_strategy()
        if prev_strat != self.strategy:
            print 'Change strat: %s' % self.strategy

    def get_output_vector(self):
        return self.strategy.get_output_vector()

    def find_optimal_strategy(self):
        max_score = 0
        strategy = self.strats[0]
        for s in self.strats:
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


class GoForBoost(Strategy):
    def __init__(self):
        self.target = self.boost_tracker.closest_big_boost

    def get_output_vector(self):
        angle_to_target = math.atan2((self.target - self.player).ground_coords)
        turn = correction_yaw(angle_to_target, self.player.foward)
        return output_vector(turn, boost=1)

    def score(self):
        # maybe 0.2 - boost? (with a maximum of 0.8)
        return 1 - round(self.player.boost / 100)


class GoForBall(Strategy):
    # GROUND BALL CHASING ONLY
    # Jumping and dodging occurs in AttemptAerial
    def get_output_vector(self):
        angle_to_ball = math.atan2((self.ball - self.player).ground_coords)
        # TODO: take velocity of ball into accord, calculating point of contact
        turn = correction_yaw(angle_to_ball, self.player.forward)
        # Determine if we should use boost
        boost = 0
        return output_vector(turn, boost=boost)

    def score(self):
        # TODO
        # if ball_hit == own_goal:
        #    return 0
        return 0.9


class GoToGoal(Strategy):
    def __init__(self):
        self.target = self.player.goal_coords

    def get_output_vector(self):
        angle_to_target = math.atan2((self.target - self.player).ground_coords)
        turn = correction_yaw(angle_to_target, self.player.foward)
        # boost or no boost?
        return output_vector(turn, boost=1)

    def score(self):
        # TODO
        return what


class IdleInCircles(Strategy):
    pass


class AttemptAerial(Strategy):
    pass
