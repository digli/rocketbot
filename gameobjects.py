import math
from constants import *
from utils import vec3, Rotation

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


class Car(KineticObject):
    def __init__(self):
        super().__init__()
        self.boost = 0
        self.speed = 0
        self.forward = 0
        self.pitch = 0
        self.rotation = Rotation()
        self.max_speed = 0

    def update(self, input):
        self.read_input(input)
        self.speed = self.velocity.length()
        self.forward = self.rotation.yaw()
        self.pitch = self.rotation.pitch()
        if self.speed > self.max_speed:
            # print('{} max speed: {}'.format(self, self.speed))
            self.max_speed = self.speed

    def below_max_speed(self):
        return self.speed < CAR_SUPERSONIC_THRESHOLD

    def should_powerslide(self, angle):
        return self.on_ground() and abs(angle) > POWERSLIDE_THRESHOLD

    def should_dodge_to(self, target):
        """:param target: Ball or vec3"""
        # TODO: split up into should_dodge_to_ball and should_dodge_to_position
        if not self.on_ground():
            return False
        if isinstance(target, Ball):
            return self.should_dodge_to_ball(target)
        if isinstance(target, vec3):
            return self.should_dodge_to_position(target)
        # Shouldnt ever come here
        print('{} is neither Ball nor vec3, not dodging'.format(target))
        return False

    def should_dodge_to_ball(self, ball):
        speed_ok = MIN_DODGE_SPEED < self.speed < CAR_MAX_SPEED - 10
        angle_to_target = self.angle_to(ball)
        relative_velocity = self.relative_velocity_to(ball)
        if relative_velocity == 0 or abs(angle_to_target) > 0.1:
            return False
        distance_to_ball = (self.position - ball.position).length()
        # TODO: factor in ball's velocity
        time_to_ball_impact = (distance_to_ball - BALL_RADIUS) / relative_velocity
        within_impact_range = relative_velocity > 0 and time_to_ball_impact < 1
        target_too_close = relative_velocity > 0 and time_to_ball_impact < 2.5
        return within_impact_range or (speed_ok and not target_too_close)

    def should_dodge_to_position(self, target):
        speed_ok = MIN_DODGE_SPEED < self.speed < CAR_MAX_SPEED - 10
        relative_velocity = self.relative_velocity_to(target)
        angle_to_target = self.angle_to(target)
        if relative_velocity == 0 or abs(angle_to_target) > 0.1:
            return False
        distance_to_target = (self.position - target).length()
        target_too_close = distance_to_target / relative_velocity < 3
        return speed_ok and not target_too_close

    def angle_to(self, target):
        """:param target: vec3 or KineticObject"""
        # TODO: vec3 angles? using rotation.forward or whatever
        if isinstance(target, KineticObject):
            target = target.position
        direction = target - self.position
        angle_to_target = math.atan2(direction.x, direction.z)
        diff = self.forward - angle_to_target
        return math.atan2(math.sin(diff), math.cos(diff))

    def closest_bumper(self, target):
        """:param target: vec3"""
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

    def is_airbound(self):
        return not self.on_wall() and not self.on_ground()

    def on_wall(self):
        on_x_wall = abs(self.position.x) > FIELD_HALF_X - CAR_HEIGHT_THRESHOLD
        on_z_wall = abs(self.position.z) > FIELD_HALF_Z - CAR_HEIGHT_THRESHOLD
        car_normal = self.rotation.up.y
        return (on_x_wall or on_z_wall) and abs(car_normal) < 0.1 

    def on_ground(self):
        return self.position.y < CAR_HEIGHT_THRESHOLD

    def relative_velocity_to(self, other):
        """:param other: KineticObject OR vec3"""
        if isinstance(other, KineticObject):
            pos = other.position - self.position 
            vel = other.velocity - self.velocity
            distance = pos.length()
            if distance == 0:
                return 0
            return (pos.x * vel.x + pos.z * vel.z) / distance
        if isinstance(other, vec3):
            return self.speed * math.cos(self.angle_to(other))
        raise TypeError('"other" must be KineticObject or vec3')

class Orange(Car):
    def __init__(self):
        super().__init__()
        self.goal_coords = vec3(z=FIELD_HALF_Z)

    def read_input(self, input):
        self.boost = input[0][37]
        self.position.set(x=input[0][18], y=input[0][17], z=input[0][3])
        self.velocity.set(x=input[0][34], y=input[0][35], z=input[0][36])
        self.rotation.values = [r for r in input[0][19:28]]


class Blue(Car):
    def __init__(self):
        super().__init__()
        self.goal_coords = vec3(z=-FIELD_HALF_Z)

    def read_input(self, input):
        self.boost = input[0][0]
        self.position.set(x=input[0][5], y=input[0][4], z=input[0][1])
        self.velocity.set(x=input[0][28], y=input[0][29], z=input[0][30])
        self.rotation.values = [r for r in input[0][8:17]]


class Ball(KineticObject):
    def __init__(self):
        super().__init__()
        self.next_bounce = 0

    def update(self, input):
        self.position.set(x=input[0][7], y=input[0][6], z=input[0][2])
        self.velocity.set(x=input[0][31], y=input[0][32], z=input[0][33])
        self.ground_direction = math.atan2(self.velocity.x, self.velocity.z)
        self.next_bounce = 0 if self.reachable_from_ground() else self.time_to_ground_hit()

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
