import math
from constants import *

class output:
    # yaw, pitch and speed will be clamped to [-1, 1]
    def __init__(self, yaw=0, pitch=0, speed=1, jump=False, boost=False, powerslide=False):
        self.yaw = yaw
        self.pitch = pitch
        self.speed = speed
        self.jump = jump
        self.boost = boost
        self.powerslide = powerslide

    def normalize_stick(self, value):
        return self.clamp(STICK_MIDDLE + STICK_MIDDLE * value)

    def clamp(self, value):
        return min(max(int(value), STICK_MIN), STICK_MAX)

    def generate_vector(self):
        return [
            self.normalize_stick(self.yaw),
            self.normalize_stick(self.pitch),
            self.clamp(self.speed * STICK_MAX) if self.speed > 0 else 0,
            self.clamp(abs(self.speed) * STICK_MAX) if self.speed < 0 else 0,
            int(self.jump),
            int(self.boost),
            int(self.powerslide)
        ]


class vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)

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
        length = self.length()
        if length == 0:
            print('Cant normalize vec3, length is 0')
            return None
        self.x /= length
        self.y /= length
        self.z /= length

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

    def pitch(self):
        return self.values[6]

    def forward(self):
        # Returns a world space angle on x,z plane
        return math.atan2(self.values[0], self.values[3])

    def up(self):
        # Returns normalized vec3 facing up
        print('Rotation.up not implemented')
        pass
