from car import Blue

class agent:
    def __init__(self, team):
        self.team = team
        self.car = Blue()
        self.max_x = 0
        self.min_x = 0

    def get_bot_name(self):
        return "PassiveAgent"

    def get_output_vector(self, input):
        self.car.read_input(input)
        if self.car.position.x > self.max_x:
            self.max_x = self.car.position.x
            print('max_x: {}'.format(self.max_x))
        if self.car.position.x < self.min_x:
            self.min_x = self.car.position.x
            print('min_x: {}'.format(self.min_x))
        return [16383, 16383, 0, 0, 0, 0, 0]
