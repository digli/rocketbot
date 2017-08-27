from gameobjects import Blue, Orange, Ball
from boost import BoostTracker
from utils import output
from strategy import StrategyManager
import emergency

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

sys.path.insert(0, os.path.abspath("../diglibot"))

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
            self.player = Blue()
            self.opponent = Orange()
        else:
            self.player = Orange()
            self.opponent = Blue()
        self.ball = Ball()
        self.boost_tracker = BoostTracker(self.player, self.opponent)
        self.strategy_manager = StrategyManager(self)
        self.previous_output = output().generate_vector()

    def get_bot_name(self):
        return "DigliBot"

    def get_output_vector(self, input):
        self.player.update(input)
        self.opponent.update(input)
        self.ball.update(input)
        self.boost_tracker.update()
        self.strategy_manager.update()

        self.previous_output = self.strategy_manager.get_output()
        return self.previous_output.generate_vector()

    def noflip(self):
        """Trigger NoFlip
        :return: output object
        """
        return self.trigger_emergency(emergency.NoFlip(self))

    def dodge(self, target):
        """Trigger DodgeTowards
        :param target: vec3
        :return: output object
        """
        return self.trigger_emergency(emergency.DodgeTowards(self, target))

    def trigger_emergency(self, emergency):
        """Trigger an emergency
        :param emergency: EmergencyStrategy
        :return: output object
        """
        self.strategy_manager.emergency_strategy = emergency
        return emergency.get_output()
