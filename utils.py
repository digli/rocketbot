import math

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Vector3(self.x - other.x,
                       self.y - other.y,
                       self.z - other.z)

    def __add__(self, other):
        return Vector3(self.x + other.x,
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
        return Vector3(self.x, self.y, self.z)

    def normalize():
        # fancy algo
        pass

    def __getitem__(self, swizzle):
        return tuple([self[c] for c in swizzle])

    @property
    def zx(self):
        return (self.z, self.x)


class Rotation:
    def __init__(self):
        self.values = []

    @property
    def forward(self):
        # Returns normalized Vector3 (disregarding y) facing forward
        return math.atan2(self.values[0], self.values[3])
        # alternative
        cos_phi = self.values[3]
        sin_phi = self.values[0]
        return Vector3(x=cos_phi, z=sin_phi)

    @property
    def up(self):
        # Returns normalized Vector3 facing up
        pass


class Orange(Car):
    def __init__(self):
        # Set goal coordinates etc

    def update(self, input):
        pass

class Blue(Car):
    def __init__(self):
        # Set goal coordinates etc

    def update(self, input):
        self.boost = input[0][0]
        px = input[0][5]
        py = input[0][4]
        pz = input[0][1]
        self.position.set(px, py, pz)
        vx = input[0][28]
        vy = input[0][29]
        vz = input[0][30]
        self.velocity.set(vx, vy, vz)
        self.rotation.values = [i for i in input[0][8:16]]


class Car:
    def __init__(self):
        self.boost = 0
        self.position = Vector3()
        self.velocity = Vector3()
        self.rotation = Rotation()

    @property
    def forward(self):
        return self.rotation.forward


class Ball:
    def __init__(self):
        self.position = Vector3()
        self.velocity = Vector3()

    def update(self, input):
        self.position.set(input[0][7], input[0][2], input[0][6])
        self.velocity.set(input[0][31], input[0][32], input[0][33])
