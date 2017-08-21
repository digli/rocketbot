import math
from utils import Blue, Orange, Ball
from boost import BoostTracker
from strategy import StrategyManager

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

boost_tracker = BoostTracker()
ball = Ball()

class agent:
    def __init__(self, team):
        self.team = team
        if team == 'blue':
            self.player = Blue()
            self.opponent = Orange()
        else:
            self.player = Orange()
            self.opponent = Blue()
        self.strategy_manager = StrategyManager(self.player, self.opponent,
                                                ball, boost_tracker)

    def get_bot_name(self):
        return "RocketBot"

    def get_output_vector(self, input):
        self.player.update(input)
        self.opponent.update(input)
        ball.update(input)
        boost_tracker.update()
        self.strategy_manager.update()

        return self.strategy_manager.get_output_vector()
