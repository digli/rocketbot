import math


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

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


class Rotation:
    def __init__(self):
        self.values = []
        # values[0]: sin(phi) ( WORLD SPACE )
        # values[1]: car.up == world.up ? cos(phi) : -cos(phi)
        # values[2]: 
        # values[3]: cos(phi) ( WORLD SPACE )
        # values[4]: car.up == world.up ? sin(phi) : -sin(phi)
        # values[5]: 
        # values[6]: 
        # values[7]: 
        # values[8]: 

    @property
    def forward(self):
        # alternative
        return math.atan2(self.values[0], self.values[3])
        # Returns normalized vec3 (disregarding y) facing forward
        cos_phi = self.values[3]
        sin_phi = self.values[0]
        return vec3(x=cos_phi, z=sin_phi)

    @property
    def up(self):
        # Returns normalized vec3 facing up
        pass


class Car:
    def __init__(self):
        self.boost = 0
        self.position = vec3()
        self.velocity = vec3()
        self.rotation = Rotation()

    @property
    def speed(self):
        return self.velocity.length

    @property
    def forward(self):
        return self.rotation.forward

class Orange(Car):
    goal_coords = vec3(z=100)

    def update(self, input):
        self.boost = input[0][37]
        px = input[0][18]
        py = input[0][17]
        pz = input[0][3]
        self.position.set(px, py, pz)
        vx = input[0][34]
        vy = input[0][35]
        vz = input[0][36]
        self.velocity.set(vx, vy, vz)
        self.rotation.values = [r for r in input[0][19:28]]

class Blue(Car):
    goal_coords = vec3(z=-100)

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
        self.rotation.values = [r for r in input[0][8:17]]


class Ball:
    def __init__(self):
        self.position = vec3()
        self.velocity = vec3()

    def update(self, input):
        self.position.set(x=input[0][7], y=input[0][6], z=input[0][2])
        self.velocity.set(x=input[0][31], y=input[0][32], z=input[0][33])

    @property
    def ground_direction(self):
        return math.atan2(self.velocity.x, self.velocity.z)

    def reachable_from_ground(self):
        return self.position.y < 4

    def next_bounce(self):
        # return ground coordinates? (z, x)
        pass
