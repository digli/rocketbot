import math
from constants import *
from utils import vec3, world, KineticObject, Rotation
from ball import Ball


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

    def update_cached_calculations(self, agent):
        # inherently flawed as we're changing intersect point later on. what do?
        self.time_to_ball = self.calculate_time_to_ball(agent.ball)
        intersect = self.calculate_intersection_point(agent.ball, self.time_to_ball)
        desired_ball_direction = agent.opponent.goal_coords - intersect
        # TODO: factor in deceleration to ball.velocity
        desired_impact_direction = desired_ball_direction - agent.ball.velocity 
        self.desired_ball_impact_speed = desired_impact_direction.length()
        # account for ball radius
        required_impact_angle = desired_impact_direction.ground_direction() + math.pi
        intersect.x += BALL_RADIUS * math.sin(required_impact_angle) * 0.6
        intersect.z += BALL_RADIUS * math.cos(required_impact_angle) * 0.6
        # we probably want to translate intersect to (car - closest_edge/corner)
        # how to factor in car.forward?
        self.will_hit_ball = (self.time_to_ball < 10
            and -FIELD_HALF_Z < intersect.z < FIELD_HALF_Z
            and -FIELD_HALF_X < intersect.x < FIELD_HALF_X)
        self.ball_intersection_point = intersect
        self.optimal_boost = agent.boost_tracker.find_optimal_boost()

    def turn_radius(self):
        # HYPOTHETICAL VALUES
        if self.speed < CAR_MAX_SPEED_WITHOUT_BOOST:
            return CAR_TURN_RADIUS
        radius_increase = CAR_TURN_RADIUS - CAR_BOOST_TURN_RADIUS
        increase_ammount = (self.speed - CAR_MAX_SPEED_WITHOUT_BOOST) / \
            (CAR_MAX_SPEED - CAR_MAX_SPEED_WITHOUT_BOOST)
        return CAR_TURN_RADIUS + increase_ammount / radius_increase

    def below_max_speed(self):
        return self.speed < CAR_SUPERSONIC_THRESHOLD

    def should_powerslide(self, angle):
        return self.on_ground() and abs(angle) > POWERSLIDE_THRESHOLD

    def boost_needed(self, delta_time):
        return delta_time * BOOST_CONSUMPTION_RATE

    def should_boost(self):
        return self.below_max_speed() and not self.is_airbound()

    def is_airbound(self):
        return not self.on_wall() and not self.on_ground()

    def on_ground(self):
        return self.position.y < CAR_HEIGHT_THRESHOLD

    def on_wall(self):
        # This will return True mid-air every now and then
        return abs(self.rotation.up.y) < 0.01
        # TODO
        on_x_wall = abs(self.position.x) > FIELD_HALF_X - CAR_HEIGHT_THRESHOLD
        on_z_wall = abs(self.position.z) > FIELD_HALF_Z - CAR_HEIGHT_THRESHOLD
        car_normal = self.rotation.up.y
        return (on_x_wall or on_z_wall) and abs(car_normal) < 0.01

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
        within_impact_range = 0.07 < self.time_to_ball < 0.1 or self.speed < ball.ground_speed
        angle = abs(self.angle_to(ball))
        return within_impact_range and ball.reachable_from_ground() and angle < 0.2

    def should_dodge_to_position(self, target):
        angle_to_target = self.angle_to(target)
        if abs(angle_to_target) > 0.01:
            return False
        speed_ok = MIN_DODGE_SPEED < self.speed < MAX_DODGE_SPEED
        time_to_target = self.dodge_mock().calculate_time_to_point(target)
        return speed_ok and time_to_target > FULL_DODGE_DURATION

    def angle_to(self, target):
        # TODO: vec3 angles? using rotation.forward or whatever
        if hasattr(target, 'position'):
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

    def calculate_time_to_ball(self, ball):
        # https://www.gamedev.net/forums/topic/647810-intersection-point-of-two-vectors/
        c = self.position
        d1 = self.velocity
        d2 = ball.velocity
        if d1.z * d2.x - d1.x * d2.z == 0:
            return math.inf
        return (c.x * d2.z - c.z * d2.x) / d1.z * d2.x - d1.x * d2.z

    def calculate_time_to_point(self, target):
        relative_velocity = self.speed * math.cos(self.angle_to(target))
        if relative_velocity == 0:
            return math.inf
        return (self.position - target).length() / relative_velocity

    def calculate_intersection_point(self, ball, dt):
        if dt < 0:
            return ball.position
        x = ball.position.x + ball.velocity.x * min(dt, 2)
        z = ball.position.z + ball.velocity.z * min(dt, 2)
        return vec3(x, ball.position.y, z)


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
