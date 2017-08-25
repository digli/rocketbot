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
        self.forward = 0
        self.pitch = 0

    def update(self, input):
        self.read_input(input)
        self.speed = self.velocity.length()
        self.forward = self.rotation.forward
        self.pitch = self.rotation.pitch

    def __str__(self):
        return self.__class__.__name__

    def below_max_speed(self):
        # Add threshold?
        return self.speed < CAR_MAX_SPEED - CAR_MAX_SPEED_THRESHOLD

    def should_powerslide(self, angle):
        return self.on_ground() and abs(angle) < POWERSLIDE_THRESHOLD

    def should_dodge_to(self, target):
        going_too_fast = self.speed > CAR_MAX_SPEED - 5
        # Factor in velocity somehow
        target_too_close = (self.position - target).length_squared() < 30**2
        going_too_slow = self.speed < MIN_DODGE_SPEED
        if going_too_fast or target_too_close or going_too_slow:
            return False
        return True

    def angle_to(self, target_position):
        direction = target_position - self.position
        angle_to_target = math.atan2(direction.x, direction.z)
        diff = self.forward - angle_to_target
        return math.atan2(math.sin(diff), math.cos(diff))

    def closest_bumper(self, target):
        diff = angle.car_to_target(self, target)
        return self.left_bumper() if diff > 0 else self.right_bumper()

    def left_bumper(self):
        angle = self.forward + math.pi / 2.0 + ANGLE_TO_BUMPER
        x = math.sin(angle) * OCTANE_MID_TO_CORNER
        z = math.cos(angle) * OCTANE_MID_TO_CORNER
        return vec3(x, OCTANE_HEIGHT, z)

    def right_bumper(self):
        angle = self.forward + math.pi / 2.0 - ANGLE_TO_BUMPER
        x = math.sin(angle) * OCTANE_MID_TO_CORNER
        z = math.cos(angle) * OCTANE_MID_TO_CORNER
        return vec3(x, OCTANE_HEIGHT, z)

    def on_ground(self):
        return self.position.y < 0.1 # arbitrary testing number

    def relative_velocity_to(self, other):
        # Not tested, stolen from GooseFairy
        pos = self.position - other.position
        vel = self.velocity - other.velocity
        distance = pos.length()
        if distance != 0:
            return (pos.x * vel.x + pos.z * vel.z) / distance
        else:
            return 0


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
        # with an velocity of 3.5, the ball will reach max y of 0.94 
        going_fast = abs(self.velocity.y) > 3.5
        if not going_fast and self.position.y - BALL_RADIUS < 1:
            # test these approximations someday
            return True
        return False

    def time_to_ground_hit(self):
        # good old PQ formula
        p = -2 * self.velocity.y / GRAVITY_CONSTANT
        q = -2 * self.position.y / GRAVITY_CONSTANT
        return -1 * p / 2.0 + math.sqrt((p / 2.0)**2 - q)

    def next_bounce_position(self):
        if (abs(self.velocity.y) < 0.5):
            # again, arbitrary guess
            return self.position.clone()
        dt = self.time_to_ground_hit()
        x = self.position.x + self.velocity.x * dt
        z = self.position.z + self.velocity.z * dt
        return vec3(x=x, z=z)

    def going_into_goal(self, goal_z):
        if goal_z * math.cos(self.ground_direction) < 0:
            # Opposite direction
            return False
        distance_to_wall = goal_z - self.position.z
        collision_x = self.position.x + math.tan(self.ground_direction) * distance_to_wall
        return abs(collision_x) < GOAL_HALF_WIDTH



def BallTracker:
    def __init__(self, ball):
        self.ball = ball
        self.position = ball.position
        self.velocity = ball.velocity
        self.prev_velocity = self.velocity.clone()

    def estimate_ground_friction(self):
        if self.position.y - BALL_RADIUS > 0.2 or self.velocity
