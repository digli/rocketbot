import math

class Field:
    HALF_SIZE_Z = 102.4
    HALF_SIZE_X = 81.92
    HEIGHT = 40
    # goal_width = 22% of full_field_x,  Derived from pixel measurements ^))
    GOAL_WIDTH = HALF_SIZE_X * 2 * 0.22 
    GOAL_POST_TOP_X = GOAL_WIDTH / 2
    GOAL_POST_BOT_X = -1 * GOAL_WIDTH / 2
    GOAL_HEIGHT = 6.7 # Maybe? Derived from https://www.reddit.com/r/RocketLeague/comments/3b00fn/rocket_league_physics_and_field_size/cshs8w1/

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
        self.speed = 0
        # hitbox spreadsheet says length is 1.18, what do
        self.length = 1.18
        self.width = 0.84
        # and would car center position be in (length/2, width/2) ?
        self.position = vec3()
        self.velocity = vec3()
        self.rotation = Rotation()

    def __str__(self):
        return self.__class__.__name__

    def update(self, input):
        self.read_input(input)
        self.speed = self.velocity.length()

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
        self.radius = 1.8555 # Trusting tarehart's judgement
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
        return abs(collision_x) < Field.GOAL_WIDTH / 2
