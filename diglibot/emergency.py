import time
from utils import angle, vec3, output

class EmergencyStrategy:
	# ONLY STRATEGIES THAT ABSOLUTELY NEED TO FINISH BEFORE CHANGING
	# No score() function, can only be triggered by other strategies
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
	# procedure:
	# boost all the way
	# jump, max pitch
	# upon jump_buffer_finished:
	# dodge, min pitch
	# then immediately: max pitch until stabilized
	def __init__(self, agent, target):
		self.agent = agent
		# who cares about target, STRAIGHT FORWARD WE GO
		self.target = target
        self.first_jump = time.time()
        self.buffer_between_jumps = False
        self.is_dodging = False

    def get_output_vector(self):
        now = time.time()
        jump = True
        pitch = STICK_MAX # NOSE UUUUP
        if (self.buffer_between_jumps and not self.is_dodging):
        	# Car in the air, buffer done, commence dodge
            self.is_dodging = True
            pitch = STICK_MIN
        if (not self.buffer_between_jumps and now - self.first_jump > JUMP_TO_DODGE_DT):
        	# Car in the air, need to buffer jump button
            self.buffer_between_jumps = True
            jump = False
        if (self.is_dodging and abs(self.agent.player.pitch) < 0.2):
        	# this might also be wrong, could occur way to early. Solve with timestamps?
        	# dont pitch to far my friend
        	pitch = STICK_MIDDLE + STICK_MIDDLE * self.agent.player.pitch
        	# pass
        return output.generate(pitch=pitch, boost=True, jump=jump)

	def is_finished(self):
		return self.agent.player.on_ground()

class DodgeTorwards(EmergencyStrategy):
	def __init__(self, agent, target):
        print('{!s} dodging forward'.format(self.agent.player))
		self.agent = agent
		self.target = target
        self.first_jump = time.time()
        self.buffer_between_jumps = False
        self.is_dodging = False
        self.full_dodge_duration = 2.0 # just a guess

    def get_output_vector(self):
        now = time.time()
        boost = self.player.below_max_speed() and not self.is_dodging
        jump = True
        pitch = STICK_MIDDLE
        turn = STICK_MIDDLE
        if (self.buffer_between_jumps and not self.is_dodging):
        	# Car in the air, buffer done, commence dodge
            self.is_dodging = True
            correction = angle.car_to_target(self.agent.player, self.target)
            turn = STICK_MIDDLE + STICK_MIDDLE * correction
            pitch = STICK_MIN
        if (not self.buffer_between_jumps and now - self.first_jump > JUMP_TO_DODGE_DT):
        	# Car in the air, need to buffer jump button
            self.buffer_between_jumps = True
            jump = False
        return output.generate(turn=turn, pitch=pitch, boost=boost, jump=jump)

    def is_finished(self):
    	return time.time() - self.first_jump < self.full_dodge_duration

	def suggest_next_strategy(self):
		return None
		# Try this later
		return SafeLanding(self.agent, self.target)


class SafeLanding(EmergencyStrategy):
	pass
