
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
