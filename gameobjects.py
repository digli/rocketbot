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
        self.goal_coords = vec3()
        self.rotation = Rotation()

    def update(self):
        self.speed = self.velocity.length()
        self.forward = self.rotation.yaw()
        self.pitch = self.rotation.pitch()

    def turn_radius(self):
        # HYPOTHETICAL VALUES
        if self.speed < 29: # max speed without boost
            return 10
        return 10 + self.speed / CAR_MAX_SPEED * 3

    def below_max_speed(self):
        return self.speed < CAR_SUPERSONIC_THRESHOLD

    def should_powerslide(self, angle):
        return self.on_ground() and abs(angle) > POWERSLIDE_THRESHOLD

    def boost_needed(self, delta_time):
        return delta_time * BOOST_CONSUMPTION_RATE

    def should_boost(self):
        return self.below_max_speed() and not self.is_airbound()

    def dodge_mock(self):
        mock = Car()
        mock.position = self.position.clone()
        mock.velocity = self.velocity.clone()
        mock.rotation = self.rotation
        speed_increment = min(DODGE_SPEED_INCREMENT, CAR_MAX_SPEED - self.speed)
        mock.velocity.x += math.sin(self.forward) * speed_increment
        mock.velocity.z += math.cos(self.forward) * speed_increment
        mock.update()
        return mock

    def should_dodge_to(self, target):
        """:param target: Ball or vec3"""
        if not self.on_ground() or self.on_wall() and self.position.y > 10:
            # TODO: if on_wall, we should dodge if car.forward points up
            return False
        if isinstance(target, Ball):
            return self.should_dodge_to_ball(target)
        if isinstance(target, vec3):
            return self.should_dodge_to_position(target)
        raise TypeError('{} is neither Ball nor vec3'.format(target))

    def should_dodge_to_ball(self, ball):
        speed_ok = MIN_DODGE_SPEED < self.speed < MAX_DODGE_SPEED
        within_impact_range = 0.07 < self.time_to_intersect(ball) < 0.1
        angle = abs(self.angle_to(ball))
        target_too_close = 0.5 < self.dodge_mock().time_to_intersect(ball) < FULL_DODGE_DURATION
        if within_impact_range and ball.reachable_from_ground() and angle < 0.2:
            return True
        return not target_too_close and speed_ok and angle < 0.1

    def should_dodge_to_position(self, target):
        angle_to_target = self.angle_to(target)
        if abs(angle_to_target) > 0.1:
            return False
        speed_ok = MIN_DODGE_SPEED < self.speed < MAX_DODGE_SPEED
        target_too_close = self.dodge_mock().time_to_intersect(target) < FULL_DODGE_DURATION
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

    def time_to_intersect(self, other):
        if isinstance(other, vec3):
            relative_velocity = self.speed * math.cos(self.angle_to(other))
            if relative_velocity == 0:
                return math.inf
            return (self.position - other).length() / relative_velocity
        if not isinstance(other, Ball):
            raise TypeError('param other should be either vec3 or Ball')
        # https://www.gamedev.net/forums/topic/647810-intersection-point-of-two-vectors/
        c = self.position
        d1 = self.velocity
        d2 = other.velocity
        if d1.z * d2.x - d1.x * d2.z == 0:
            return math.inf
        time_estimate = (c.x * d2.z - c.z * d2.x) / (d1.z * d2.x - d1.x * d2.z)
        if time_estimate < 0:
            # not quite sure
            # maybe just return abs(time_estimate)
            return math.inf
        return time_estimate

    def intersection_point(self, other):
        t = self.time_to_intersect(other)
        if (t == math.inf):
            return other.position
        x = other.position.x + other.velocity.x * t
        z = other.position.z + other.velocity.z * t
        return vec3(x, 0, z)


class Orange(Car):
    def __init__(self):
        super().__init__()
        self.goal_coords.z = FIELD_HALF_Z

    def read_input(self, input):
        self.boost = input[0][37]
        self.position.set(x=input[0][18], y=input[0][17], z=input[0][3])
        self.velocity.set(x=input[0][34], y=input[0][35], z=input[0][36])
        self.rotation.values = [r for r in input[0][19:28]]


class Blue(Car):
    def __init__(self):
        super().__init__()
        self.goal_coords.z = -FIELD_HALF_Z

    def read_input(self, input):
        self.boost = input[0][0]
        self.position.set(x=input[0][5], y=input[0][4], z=input[0][1])
        self.velocity.set(x=input[0][28], y=input[0][29], z=input[0][30])
        self.rotation.values = [r for r in input[0][8:17]]


class Ball(KineticObject):
    def __init__(self):
        super().__init__()
        self.next_bounce = 0
        self.ground_direction = 0
        self.ground_speed = 0

    def read_input(self, input):
        self.position.set(x=input[0][7], y=input[0][6], z=input[0][2])
        self.velocity.set(x=input[0][31], y=input[0][32], z=input[0][33])
        
    def update(self):
        self.ground_direction = math.atan2(self.velocity.x, self.velocity.z)
        self.ground_speed = math.hypot(self.velocity.x, self.velocity.z)
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
        # Need to account for 3% speed loss every second
        p = -2 * self.velocity.y / GRAVITY_CONSTANT
        q = -2 * self.position.y / GRAVITY_CONSTANT - BALL_RADIUS
        if (p / 2.0)**2 < q:
            # prevent negative sqrt
            return 0
        return -1 * p / 2.0 + math.sqrt((p / 2.0)**2 - q)

    def next_bounce_position(self, dt=None):
        if (abs(self.velocity.y) < 0.5):
            return self.position.clone()
        if dt is None:
            dt = self.time_to_ground_hit()
        x = self.position.x + self.velocity.x * dt * 0.97**dt
        z = self.position.z + self.velocity.z * dt * 0.97**dt
        return vec3(x, 0, z)

    def going_into_goal(self, player):
        goal_z = player.goal_coords.z
        if goal_z * math.cos(self.ground_direction) < 0 or self.ground_speed == 0:
            # Opposite direction
            return False
        distance_to_wall = goal_z - self.position.z
        collision_x = self.position.x + math.tan(self.ground_direction) * distance_to_wall
        return abs(collision_x) < GOAL_HALF_WIDTH

    def account_for_radius(self, angle):
        position = self.position.clone()
        position.x += math.cos(angle) * BALL_RADIUS * 0.6 # test constant
        position.z += math.sin(angle) * BALL_RADIUS * 0.6
        return position

    def predict_direction_after_impact(self, car):
        impact_angle = car.angle_to(self)
        vx = self.velocity.x + math.sin(impact_angle) * car.velocity.x * CAR_FORCE
        vz = self.velocity.z + math.sin(impact_angle) * car.velocity.z * CAR_FORCE
        return math.atan2(vx, vz)

    def predict_position(self, delta_time):
        speed_loss = 0.97**delta_time
        x = self.position.x + self.velocity.x * speed_loss
        z = self.position.z + self.velocity.z * speed_loss
        y = self.position.y - BALL_RADIUS + self.velocity.y * delta_time \
            - GRAVITY_CONSTANT * delta_time**2 / 2
        return vec3(x, y, z)

    def angle_to_goal(self, goal):
        direction = goal - self.position
        angle_to_target = math.atan2(direction.x, direction.z)
        diff = self.ground_direction - angle_to_target
        return math.atan2(math.sin(diff), math.cos(diff))

    def desired_angle_to_goal(self, goal):
        return -1 * self.angle_to_goal(goal)
