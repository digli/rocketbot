import time
from utils import vec3, output
from dodgetimer import *
from constants import *

class EmergencyStrategy:
    # STRATEGIES THAT ABSOLUTELY NEED TO FINISH BEFORE CHANGING
    # No score() function, can only be triggered by other strategies
    def __init__(self, agent, target):
        # :param target: vec3
        self.agent = agent
        if not isinstance(target, vec3):
            print('{} is not vec3'.format(target))
        self.target = target
        print('{!s} initiated emergency {!s}'.format(agent.player, self))

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
    def __init__(self, agent, target):
        super().__init__(agent, None)
        # KickOff target should be somewhere in front of ball
        self.target = vec3(z=self.agent.player.goal_coords.z * 0.05)
        self.starting_position = self.agent.player.position.clone()

    def get_output(self):
    	angle = self.player.angle_to(self.target)
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
    def __init__(self, agent, target):
        super().__init__(agent, target)
        self.dodge_timer = DodgeTimer(d0=0.37)

    def get_output(self):
        pitch = STICK_MAX
        dodge_state = self.dodge_timer.update_state()
        boost = self.agent.player.below_max_speed() and dodge_state != JUMP_BUFFERING
        jump = self.dodge_timer.jump_button()
        if (dodge_state == JUMP_DODGING):
            pitch = STICK_MIN
        return output(pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
        # arbitrary again
        return time.time() - self.dodge_timer.start > 1.7 and self.agent.player.on_ground()

    def suggest_next_strategy(self):
        return DodgeTowards(self.agent, self.target)
        return Idle(self.agent, self.target)

class DodgeTowards(EmergencyStrategy):
    def __init__(self, agent, target):
        super().__init__(agent, target)
        self.dodge_timer = DodgeTimer()

    def get_output(self):
        pitch = STICK_MIDDLE
        turn = STICK_MIDDLE
        dodge_state = self.dodge_timer.update_state()
        boost = self.agent.player.below_max_speed() and dodge_state < JUMP_DODGING
        jump = self.dodge_timer.jump_button()
        if dodge_state == JUMP_DODGING:
        	angle = self.player.angle_to(self.target)
        	turn = angle * YAW_SENSITIVITY
            pitch = STICK_MIN # Nose down, maximum velocity here we go
        return output(yaw=turn, pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
        return self.dodge_timer.is_finished() and self.agent.player.on_ground()

    def suggest_next_strategy(self):
        return None
        # return None
        return Idle(self.agent, self.target)
        # Try this later
        return SafeLanding(self.agent, self.target)


class Idle(EmergencyStrategy):
    def __init__(self, agent, target):
        super().__init__(agent, target)
        self.timestamp = time.time()

    def get_output(self):
        return output(speed=0)

    def is_finished(self):
        return time.time() - self.timestamp > 2

    def suggest_next_strategy(self):
        return NoFlip(self.agent, self.target)

class SafeLanding(EmergencyStrategy):
    pass
