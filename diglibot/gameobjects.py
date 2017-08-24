import math
from constants import *
from utils import vec3, Rotation


class Car:
    def __init__(self):
        self.boost = 0
        self.speed = 0
        self.position = vec3()
        self.velocity = vec3()
        self.rotation = Rotation()

    def __str__(self):
        return self.__class__.__name__

    def below_max_speed(self):
        # Add threshold?
        return self.speed < CAR_MAX_SPEED

    def update(self, input):
        self.read_input(input)
        self.speed = self.velocity.length()

    def on_ground(self):
        return self.position.y < 0.5 # arbitrary testing number

    @property
    def pitch(self):
        return self.rotation.pitch

    @property
    def forward(self):
        return self.rotation.forward


class Orange(Car):
    def __init__(self):
        super().__init__()
        self.goal_coords = vec3(z=102.4)

    def read_input(self, input):
        self.boost = input[0][37]
        self.position.set(x=input[0][18], y=input[0][17], z=input[0][3])
        self.velocity.set(x=input[0][34], y=input[0][35], z=input[0][36])
        self.rotation.values = [r for r in input[0][19:28]]


class Blue(Car):
    def __init__(self):
        super().__init__()
        self.goal_coords = vec3(z=-102.4)

    def read_input(self, input):
        self.boost = input[0][0]
        self.position.set(x=input[0][5], y=input[0][4], z=input[0][1])
        self.velocity.set(x=input[0][28], y=input[0][29], z=input[0][30])
        self.rotation.values = [r for r in input[0][8:17]]


class Ball:
    def __init__(self):
        self.position = vec3()
        self.velocity = vec3()

    def update(self, input):
        self.position.set(x=input[0][7], y=input[0][6], z=input[0][2])
        self.velocity.set(x=input[0][31], y=input[0][32], z=input[0][33])
        self.ground_direction = math.atan2(self.velocity.x, self.velocity.z)

    def reachable_from_ground(self):
        return self.position.y < 4

    def next_bounce(self):
        # return ground coordinates? (z, x)
        pass

    def going_into_goal(self, goal_z):
        if goal_z * math.cos(self.ground_direction) < 0:
            # Opposite direction
            return False
        distance_to_wall = goal_z - self.position.z
        collision_x = self.position.x + math.tan(self.ground_direction) * distance_to_wall
        return abs(collision_x) < GOAL_HALF_WIDTH
