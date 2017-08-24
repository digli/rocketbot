import time
from utils import angle, vec3, output
from dodgetimer import *
from constants import *

class EmergencyStrategy:
    # STRATEGIES THAT ABSOLUTELY NEED TO FINISH BEFORE CHANGING
    # No score() function, can only be triggered by other strategies
    def __init__(self, agent, target):
        # :param target: vec3
        self.agent = agent
        self.target = target
        print('{!s} initiated emergency {!s}'.format(agent.player, self))

    def get_output_vector(self):
        print('{!s} missing implementation: get_output_vector()'.format(self))
        pass

    def is_finished(self):
        print('{!s} missing implementation: is_finished()'.format(self))
        pass

    def suggest_next_strategy(self):
        return None

    def __str__(self):
        return self.__class__.__name__


class KickOff(EmergencyStrategy):
    # TODO
    # Boost towards ball (speed-dodge?), dodge into ball
    # Maybe dont dodge if other player is far away?
    # also, dodge ball into goal angle?
    pass


class NoFlip(EmergencyStrategy):
    # Also known as Air Dash
    # Ok so this works well IF player has boost
    def __init__(self, agent, target):
        super().__init__(agent, target)
        self.dodge_timer = DodgeTimer(d0=0.37)

    def get_output_vector(self):
        pitch = STICK_MAX
        dodge_state = self.dodge_timer.update_state()
        boost = self.agent.player.below_max_speed() and dodge_state != JUMP_BUFFERING
        jump = self.dodge_timer.jump_button()
        if (dodge_state == JUMP_DODGING):
            pitch = STICK_MIN
        return output.generate(pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
        return time.time() - self.dodge_timer.start > 1.7 # arbitrary again
        return self.dodge_timer.is_finished()
        return self.agent.player.on_ground()

    def suggest_next_strategy(self):
        return Idle(self.agent, self.target)

class DodgeTowards(EmergencyStrategy):
    def __init__(self, agent, target):
        super().__init__(agent, target)
        self.dodge_timer = DodgeTimer()

    def get_output_vector(self):
        pitch = STICK_MIDDLE
        turn = STICK_MIDDLE
        dodge_state = self.dodge_timer.update_state()
        boost = self.agent.player.below_max_speed() and dodge_state < JUMP_DODGING
        jump = self.dodge_timer.jump_button()
        if dodge_state == JUMP_DODGING:
            correction = angle.car_to_target(self.agent.player, self.target)
            turn = int(STICK_MIDDLE + STICK_MIDDLE * correction)
            turn = min(max(turn, STICK_MIN), STICK_MAX)
            pitch = STICK_MIN # Nose down, maximum velocity here we go
        return output.generate(yaw=turn, pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
        return self.dodge_timer.is_finished()

    def suggest_next_strategy(self):
        # return None
        return Idle(self.agent, self.target)
        # Try this later
        return SafeLanding(self.agent, self.target)


class Idle(EmergencyStrategy):
    def __init__(self, agent, target):
        super().__init__(agent, target)
        self.timestamp = time.time()

    def get_output_vector(self):
        return output.generate(speed=0)

    def is_finished(self):
        return time.time() - self.timestamp > 2

    def suggest_next_strategy(self):
        return NoFlip(self.agent, self.target)

class SafeLanding(EmergencyStrategy):
    pass
