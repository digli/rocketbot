from utils import output
from strategy import StrategyManager
import boost
import emergency
import car
import ball

'''
Hi! You can use this code as a template to create your own bot.  
Also if you don't mind writing a blurb about your bot's strategy
you can put it as a comment here. I'd appreciate it, especially if 
I can help debug any runtime issues that occur with your bot.

__insert_later__
'''

# Your real name: Elliot Jalgard
# Contact Email: __insert_later__
# Can this bot's code be shared publicly: Yes
# Can non-tournment gameplay of this bot be displayed publicly: Yes

"""
# runner.py setup
############ DigliBot
import sys
import os

sys.path.insert(0, os.path.abspath("./diglibot"))

from diglibot import DigliBot
from diglibot import PassiveAgent

agent1 = DigliBot.agent('blue')
agent2 = DigliBot.agent("orange")
# agent1 = PassiveAgent.agent('blue')
# agent2 = PassiveAgent.agent('orange')
############ /DigliBot
"""


class agent:
    def __init__(self, team):
        self.team = team
        if team == 'blue':
            self.player = car.Blue()
            self.opponent = car.Orange()
        else:
            self.player = car.Orange()
            self.opponent = car.Blue()
        self.ball = ball.Ball()
        self.boost_tracker = boost.BoostTracker(self.player, self.opponent)
        self.strategy_manager = StrategyManager(self)
        self.previous_output = output()

    def get_bot_name(self):
        return "DigliBot"

    def get_output_vector(self, input):
        self.player.read_input(input)
        self.opponent.read_input(input)
        self.ball.read_input(input)

        self.player.update()
        self.opponent.update()
        self.player.update_cached_calculations(self)
        self.opponent.update_cached_calculations(self)
        self.ball.update()
        self.boost_tracker.update()
        self.strategy_manager.update()

        self.previous_output = self.strategy_manager.get_output()
        return self.previous_output.generate_vector()

    def noflip(self):
        return self.trigger_emergency(emergency.NoFlip(self))

    def dodge(self, target):
        return self.trigger_emergency(emergency.DodgeForSpeed(self, target))

    def trigger_emergency(self, emergency):
        self.strategy_manager.emergency_strategy = emergency
        return emergency.get_output()
