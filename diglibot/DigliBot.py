from gameobjects import Blue, Orange, Ball
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
        self.boost_tracker = BoostTracker(self.player, self.opponent)
        self.strategy_manager = StrategyManager(self)

    def get_bot_name(self):
        return "DigliBot"

    def get_output_vector(self, input):
        self.player.update(input)
        self.opponent.update(input)
        self.ball.update(input)
        self.boost_tracker.update()
        self.strategy_manager.update()

        return self.strategy_manager.get_output_vector()

    def trigger_emergency(self, emergency):
        self.strategy_manager.emergency_strategy = emergency
