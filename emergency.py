import time
from constants import *
from dodgetimer import DodgeTimer
from utils import vec3, output


class EmergencyStrategy:
    # STRATEGIES THAT ABSOLUTELY NEED TO FINISH BEFORE CHANGING
    # No score() function, can only be triggered by other strategies
    def __init__(self, agent):
        self.agent = agent
        print('{}\tchanged strat to {}'.format(agent.player, self))

    def get_output(self):
        print('{} missing implementation: get_output()'.format(self))
        return output()

    def is_finished(self):
        print('{} missing implementation: is_finished()'.format(self))
        return True

    def suggest_next_strategy(self):
        return None

    def __str__(self):
        return self.__class__.__name__


class KickOff(EmergencyStrategy):
    def __init__(self, agent):
        super().__init__(agent)
        # KickOff target should be somewhere in front of ball
        self.target = vec3(z=math.copysign(BALL_RADIUS, self.agent.player.goal_coords.z))

    def get_output(self):
        angle = self.agent.player.angle_to(self.target)
        turn = angle * KICKOFF_YAW_SENSITIVITY
        return output(yaw=turn, boost=True)

    def is_finished(self):
        return 1.8 < self.agent.player.dodge_mock().time_to_intersect(self.target) < 2.2

    def suggest_next_strategy(self):
        return DodgeForSpeed(self.agent, self.target)


class NoFlip(EmergencyStrategy):
    def __init__(self, agent):
        super().__init__(agent)
        self.dodge_timer = DodgeTimer(d0=0.37)

    def get_output(self):
        dodge_state = self.dodge_timer.update_state()
        boost = self.agent.player.below_max_speed() and dodge_state != JUMP_BUFFERING
        jump = self.dodge_timer.jump_button()
        pitch = -1 if dodge_state == JUMP_DODGING else 1
        return output(pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
        return (time.time() - self.dodge_timer.start > FULL_DODGE_DURATION or
            self.dodge_timer.is_finished() and not self.agent.player.is_airbound())


class DodgeForSpeed(EmergencyStrategy):
    def __init__(self, agent, target):
        super().__init__(agent)
        self.target = target
        self.dodge_timer = DodgeTimer()

    def get_output(self):
        dodge_state = self.dodge_timer.update_state()
        pitch = -1 * (dodge_state == JUMP_DODGING)
        turn = 0
        if dodge_state == JUMP_DODGING:
            turn = self.agent.player.angle_to(self.target) * DODGE_SENSITIVITY
        boost = not self.dodge_timer.is_finished()
        jump = self.dodge_timer.jump_button()
        return output(yaw=turn, pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
        return (time.time() - self.dodge_timer.start > FULL_DODGE_DURATION or
            self.dodge_timer.is_finished() and not self.agent.player.is_airbound())


class DodgeIntoBall(EmergencyStrategy):
    # TBD: is this needed? (not used atm)
    def __init__(self, agent, ball):
        super().__init__(agent)
        self.ball = ball
        self.dodge_timer = DodgeTimer()

    def get_output(self):
        pitch = 0
        turn = 0
        dodge_state = self.dodge_timer.update_state()
        boost = self.agent.player.below_max_speed() and dodge_state < JUMP_DODGING
        jump = self.dodge_timer.jump_button()
        if dodge_state == JUMP_DODGING:
            angle = self.agent.player.angle_to(self.target)
            turn = angle * DODGE_SENSITIVITY
            pitch = -1 # Nose down, maximum velocity here we go
        return output(yaw=turn, pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
        return (time.time() - self.dodge_timer.start > FULL_DODGE_DURATION or
            self.dodge_timer.is_finished() and not self.agent.player.is_airbound())


class Idle(EmergencyStrategy):
    def __init__(self, agent):
        super().__init__(agent)
        self.timestamp = time.time()

    def get_output(self):
        return output(speed=0)

    def is_finished(self):
        return True
