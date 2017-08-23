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

    def get_bot_name(self):
        return "PassiveAgent"

    def get_output_vector(self, input):
        return [16383, 16383, 0, 0, 0, 0, 0]
