import math
from constants import *

class output:
    @classmethod
    def generate(self, yaw=STICK_MIDDLE, pitch=STICK_MIDDLE, speed=1, 
                 jump=False, boost=False, powerslide=False):
        acceleration = int(round(speed * STICK_MAX)) if speed > 0 else 0
        retardation = int(round(abs(speed) * STICK_MAX)) if speed < 0 else 0
        jump = int(jump)
        boost = int(boost)
        powerslide = int(powerslide)
        return [yaw, pitch, acceleration, retardation, jump, boost, powerslide]

class angle:
    @classmethod
    def diff(self, a1, a2):
        # Returns radian in range (-math.pi, math.pi)
        return math.atan2(math.sin(a1-a2), math.cos(a1-a2))

    @classmethod
    def car_to_target(self, car, target_position):
        direction = target_position - car.position
        angle_to_target = math.atan2(direction.x, direction.z)
        return self.diff(car.forward, angle_to_target)

class vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return vec3(self.x - other.x,
                    self.y - other.y,
                    self.z - other.z)

    def __add__(self, other):
        return vec3(self.x + other.x,
                    self.y + other.y,
                    self.z + other.z)

    def copy(self, other):
        self.x = other.x
        self.y = other.y
        self.z = other.z

    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return vec3(self.x, self.y, self.z)

    def normalize(self):
        # fancy algo
        pass

    def length_squared(self):
        # idk how slow math.sqrt is
        return self.x**2 + self.y**2 + self.z**2

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __str__(self):
        return '({}, {}, {})'.format(self.x, self.y, self.z)


class Rotation:
    def __init__(self):
        self.values = []
        # values[0]: sin(phi) ( WORLD SPACE )
        # values[1]: car.up == world.up ? cos(phi) : -cos(phi)
        # values[2]: cos(roll_x)
        # values[3]: cos(phi) ( WORLD SPACE )
        # values[4]: car.up == world.up ? sin(phi) : -sin(phi)
        # values[5]: cos(roll_z)
        # values[6]: sin(pitch)
        # values[7]: 
        # values[8]: cos(pitch&roll)

    @property
    def pitch(self):
        return self.values[6]

    @property
    def forward(self):
        # Returns a world space angle on x,z plane
        return math.atan2(self.values[0], self.values[3])

    @property
    def up(self):
        # Returns normalized vec3 facing up
        pass

