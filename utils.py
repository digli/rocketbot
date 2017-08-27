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

    def __mul__(self, other):
        # Dot product
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __gt__(self, other):
        return self.length_squared() > other.length_squared()

    def __lt__(self, other):
        return self.length_squared() < other.length_squared()

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
        self.values = [0 for i in range(0, 9)]

    def pitch(self):
        return self.values[6]

    def yaw(self):
        # Returns a world space angle on x,z plane
        return math.atan2(self.values[0], self.values[3])

    # Credit to Arator for following functions
    @property
    def forward(self):
        # Normalized vector (roll axis)
        return vec3(self.values[0], self.values[6], self.values[3])

    @property
    def right(self):
        # Normalized vector (pitch axis)
        return vec3(self.values[1], self.values[7], self.values[4])

    @property
    def up(self):
        # Normalized vector (yaw axis)
        return vec3(self.values[2], self.values[8], self.values[5])


class world:
    # z and x could be mixed up, idk yet
    forward = vec3(x=1)
    up = vec3(y=1)
    right = vec3(z=1)


class KineticObject:
    def __init__(self):
        self.position = vec3()
        self.velocity = vec3()

    def __str__(self):
        return self.__class__.__name__

    def time_to_intersect(self, other):
        # TODO: move this to Car
        # will raise exceptions if called on ball, self.speed and self.angle_to is used 
        # https://www.gamedev.net/forums/topic/647810-intersection-point-of-two-vectors/
        if other.velocity.length_squared() == 0:
            # treat other as static point
            rel_velocity = self.speed * math.cos(self.angle_to(other))
            if rel_velocity == 0:
                return 999999999
            return (self.position - other.position).length() / rel_velocity 
        c = self.position - other.position
        d1 = self.velocity
        d2 = other.velocity
        # so what, if ball has v=0, it never intersects?
        if d1.z * d2.x - d1.x * d2.z == 0:
            return 999999999 # 'infinity'
        return (c.x * d2.z - c.z * d2.x) / (d1.z * d2.x - d1.x * d2.z)

    def intersection_point(self, other):
        t = self.time_to_intersect(other)
        x = other.position.x + other.velocity.x * t
        z = other.position.z + other.velocity.z * t
        return vec3(x, 0, z)
