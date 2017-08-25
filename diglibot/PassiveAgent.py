
class agent:
    def __init__(self, team):
        self.team = team

    def get_bot_name(self):
        return "PassiveAgent"

    def get_output_vector(self, input):
        return [16383, 16383, 0, 0, 0, 0, 0]
