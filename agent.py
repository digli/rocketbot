import math

'''
Hi! You can use this code as a template to create your own bot.  Also if you don't mind writing a blurb
about your bot's strategy you can put it as a comment here. I'd appreciate it, especially if I can help
debug any runtime issues that occur with your bot.
'''

# Optional Information. Fill out only if you wish.

# Your real name:
# Contact Email:
# Can this bot's code be shared publicly (Default: No):
# Can non-tournment gameplay of this bot be displayed publicly (Default: No):

class agent:

	def __init__(self, team):
		self.team = team
		if team == 'blue':
			self.player = Blue()
			self.opponent = Orange()
		else:
			self.player = Orange()
			self.opponent = Blue()
		self.ball = Ball()

	def get_bot_name(self):
		return "RocketBot"

	def get_output_vector(self, input):
		self.ball.update(input)
		self.player.update(input)
		self.opponent.update(input)

		angle_to_ball = math.atan2((self.ball - self.player).zx)
		turn = 0 if angle_diff(angle_to_ball, self.player.forward) < 0 else 32767

		return [turn, 16383, 32767, 0, 0, 0, 0]

def angle_diff(a1, a2):
	return math.pi - abs(abs(a1 - a2) - math.pi); 
