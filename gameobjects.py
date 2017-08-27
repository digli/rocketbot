import math
from constants import *
from utils import vec3, world, KineticObject, Rotation


class Car(KineticObject):
    def __init__(self):
        super().__init__()
        self.boost = 0
        self.speed = 0
        self.forward = 0
        self.pitch = 0
        self.rotation = Rotation()

    def update(self, input):
        self.read_input(input)
        self.speed = self.velocity.length()
        self.forward = self.rotation.yaw()
        self.pitch = self.rotation.pitch()

    def below_max_speed(self):
        return self.speed < CAR_SUPERSONIC_THRESHOLD

    def should_powerslide(self, angle):
        return self.on_ground() and abs(angle) > POWERSLIDE_THRESHOLD

    def dodge_mock(self):
        v = self.velocity.clone()
        p = self.position.clone()
        angle = self.forward
        speed_increment = max(DODGE_SPEED_INCREMENT, CAR_MAX_SPEED - self.speed)
        v.x += math.sin(self.forward) * speed_increment
        v.z += math.cos(self.forward) * speed_increment
        return KineticObject(p, v)

    def should_dodge_to(self, target):
        """:param target: Ball or vec3"""
        if not self.on_ground() or self.on_wall() and self.position.y > 10:
            return False
        if isinstance(target, Ball):
            return self.should_dodge_to_ball(target)
        if isinstance(target, vec3):
            return self.should_dodge_to_position(target)
        raise TypeError('{} is neither Ball nor vec3'.format(target))

    def should_dodge_to_ball(self, ball):
        # TODO: use dodge_mock
        speed_ok = MIN_DODGE_SPEED < self.speed < CAR_MAX_SPEED - 10
        angle_to_target = self.angle_to(ball)
        relative_velocity = self.relative_velocity_to(ball)
        if relative_velocity == 0 or abs(angle_to_target) > 0.1:
            return False
        distance_to_ball = (self.position - ball.position).length()
        # TODO: factor in ball's velocity
        time_to_ball_impact = (distance_to_ball - BALL_RADIUS) / relative_velocity
        within_impact_range = relative_velocity > 0 and time_to_ball_impact < 1
        target_too_close = relative_velocity > 0 and time_to_ball_impact < 5
        target_too_close &= not ball.reachable_from_ground()
        return within_impact_range or (speed_ok and not target_too_close)

    def should_dodge_to_position(self, target):
        speed_ok = MIN_DODGE_SPEED < self.speed < CAR_MAX_SPEED - 10
        relative_velocity = self.relative_velocity_to(target)
        angle_to_target = self.angle_to(target)
        if relative_velocity == 0 or abs(angle_to_target) > 0.1:
            return False
        distance_to_target = (self.position - target).length()
        target_too_close = distance_to_target / relative_velocity < 4
        return speed_ok and not target_too_close

    def angle_to(self, target):
        """:param target: vec3 or KineticObject"""
        # TODO: vec3 angles? using rotation.forward or whatever
        if isinstance(target, KineticObject):
            target = target.position
        direction = target - self.position
        if self.on_wall():
            # Check if ball is close to wall
            # get proper angle
            pass
        angle_to_target = math.atan2(direction.x, direction.z)
        diff = self.forward - angle_to_target
        return math.atan2(math.sin(diff), math.cos(diff))

    def closest_bumper(self, target):
        """:param target: vec3"""
        diff = self.anle_to(self, target)
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
        return (on_x_wall or on_z_wall) and abs(car_normal) < 0.01

    def on_ground(self):
        return self.position.y < CAR_HEIGHT_THRESHOLD

    def relative_velocity_to(self, other):
        # Scrap this? (use time_to_intersect instead)
        """:param other: KineticObject OR vec3"""
        if isinstance(other, KineticObject):
            return (other.velocity - self.velocity) * vec3(1, 1, 1)
            pos = other.position - self.position 
            vel = other.velocity - self.velocity
            distance = pos.length()
            if distance == 0:
                return 0
            return pos * vel / distance
        if isinstance(other, vec3):
            return self.speed * math.cos(self.angle_to(other))
        raise TypeError('"other" must be KineticObject or vec3')

    def time_to_intersect(self, other):
        if other.velocity.length_squared() == 0:
            # treat other as static point
            rel_velocity = self.speed * math.cos(self.angle_to(other))
            if rel_velocity == 0:
                return 999999999
            return (self.position - other.position).length() / rel_velocity 
        # https://www.gamedev.net/forums/topic/647810-intersection-point-of-two-vectors/
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
        self.nbp = self.next_bounce_position()

    def reachable_from_ground(self):
        # with an velocity of 3.5, the ball will reach max y of 0.94 
        going_fast = abs(self.velocity.y) > 3.5
        if not going_fast and self.position.y - BALL_RADIUS < 1:
            # test these approximations someday
            return True
        return False

    def time_to_ground_hit(self):
        # good old PQ formula
        # need rework, doesnt take ball radius into account
        p = -2 * self.velocity.y / GRAVITY_CONSTANT
        q = -2 * self.position.y / GRAVITY_CONSTANT
        if (p / 2.0)**2 < q:
            # prevent negative sqrt
            return 0
        return -1 * p / 2.0 + math.sqrt((p / 2.0)**2 - q)

    def next_bounce_position(self):
        if (abs(self.velocity.y) < 0.5):
            # again, arbitrary guess
            return self.position.clone()
        dt = self.time_to_ground_hit()
        x = self.position.x + self.velocity.x * dt
        z = self.position.z + self.velocity.z * dt
        return vec3(x, 0, z)

    def going_into_goal(self, goal_z):
        if goal_z * math.cos(self.ground_direction) < 0:
            # Opposite direction
            return False
        distance_to_wall = goal_z - self.position.z
        collision_x = self.position.x + math.tan(self.ground_direction) * distance_to_wall
        return abs(collision_x) < GOAL_HALF_WIDTH
