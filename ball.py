import math
from utils import vec3, KineticObject
from constants import *


class Ball(KineticObject):
    def __init__(self):
        super().__init__()
        self.ground_direction = 0
        self.ground_speed = 0
        self.time_to_bounce = 0
        self.next_bounce_position = vec3()

    def read_input(self, input):
        self.position.set(x=input[0][7], y=input[0][6], z=input[0][2])
        self.velocity.set(x=input[0][31], y=input[0][32], z=input[0][33])
        
    def update(self):
        self.ground_direction = self.velocity.ground_direction()
        self.ground_speed = math.hypot(self.velocity.x, self.velocity.z)
        self.next_bounce = 0 if self.reachable_from_ground() else self.time_to_ground_hit()
        self.time_to_bounce = 0 if self.reachable_from_ground() else self.ball.time_to_ground_hit()
        self.next_bounce_position = self.ball.next_bounce_position(self.time_to_bounce)

    def reachable_from_ground(self):
        # with an velocity of 3.5, the ball will reach max y of 0.94 
        going_fast = abs(self.velocity.y) > 3.5
        if not going_fast and self.position.y - BALL_RADIUS < 2:
            # test these approximations someday
            return True
        return False

    def time_to_ground_hit(self):
        # good old PQ formula
        # Do we need to account for 3% speed loss every second?
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
        if self.ground_speed == 0:
            return False
        if player.goal_coords.z * math.cos(self.ground_direction) < 0:
            # Opposite direction
            return False
        distance_to_wall = player.goal_coords.z - self.position.z
        collision_x = self.position.x + math.tan(self.ground_direction) * distance_to_wall
        return abs(collision_x) < GOAL_HALF_WIDTH

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
        return math.pi + self.angle_to_goal(goal)
