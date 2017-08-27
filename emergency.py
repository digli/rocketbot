import time
from dodgetimer import *
from constants import *
from utils import vec3, output


class EmergencyStrategy:
    # STRATEGIES THAT ABSOLUTELY NEED TO FINISH BEFORE CHANGING
    # No score() function, can only be triggered by other strategies
    def __init__(self, agent):
        # :param target: vec3
        self.agent = agent
        print('{!s} changed strat to {!s}'.format(agent.player, self))

    def get_output(self):
        print('{!s} missing implementation: get_output()'.format(self))
        pass

    def is_finished(self):
        print('{!s} missing implementation: is_finished()'.format(self))
        pass

    def suggest_next_strategy(self):
        return None

    def __str__(self):
        return self.__class__.__name__


class KickOff(EmergencyStrategy):
    def __init__(self, agent):
        super().__init__(agent)
        # KickOff target should be somewhere in front of ball
        self.target = vec3(z=self.agent.player.goal_coords.z * 0.01)
        self.starting_position = self.agent.player.position.clone()

    def get_output(self):
        angle = self.agent.player.angle_to(self.target)
        turn = angle * KICKOFF_YAW_SENSITIVITY
        # Boost towards ball (speed-dodge?), dodge into ball
        # Maybe dont dodge if other player is far away?
        # also, dodge ball into goal angle?
        return output(yaw=turn, boost=True)

    def is_finished(self):
        if (self.starting_position - self.agent.player.position).length_squared() > 30**2:
            # Calibration error
            self.starting_position = self.agent.player.position.clone()
            return False
        # how long again?
        return (self.starting_position - self.agent.player.position).length_squared() > 6**2

    def suggest_next_strategy(self):
        return DodgeTowards(self.agent, self.target)


class NoFlip(EmergencyStrategy):
    # Also known as Air Dash
    # Ok so this works well IF player has boost
    # and not so well for kickoffs
    def __init__(self, agent):
        super().__init__(agent)
        self.dodge_timer = DodgeTimer(d0=0.37)

    def get_output(self):
        pitch = 1
        dodge_state = self.dodge_timer.update_state()
        boost = self.agent.player.below_max_speed() and dodge_state != JUMP_BUFFERING
        jump = self.dodge_timer.jump_button()
        if (dodge_state == JUMP_DODGING):
            pitch = -1
        return output(pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
        # arbitrary guesses
        return time.time() - self.dodge_timer.start > 1.7 and self.agent.player.on_ground()

class DodgeTowards(EmergencyStrategy):
    def __init__(self, agent, target):
        super().__init__(agent)
        self.target = target
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
        time_elapsed = time.time() - self.dodge_timer.start
        return time_elapsed > 1 and not self.agent.player.is_airbound()

    def suggest_next_strategy(self):
        return None
        # return None
        return Idle(self.agent, self.target)
        # Try this later
        return SafeLanding(self.agent, self.target)


class Idle(EmergencyStrategy):
    def __init__(self, agent):
        super().__init__(agent)
        self.timestamp = time.time()

    def get_output(self):
        return output(speed=0)

    def is_finished(self):
        return True

class SafeLanding(EmergencyStrategy):
    pass
