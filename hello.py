player
opponent
ball
boost_tracker
agent



# inherently flawed as we're changing intersect point later on. what do?
time_to_ball = player.calculate_time_to_ball(ball)
angle_to_ball = player.angle_to(ball)
if time_to_ball < 0:
	turn = angle * YAW_SENSITIVITY
	return output(yaw=turn, powerslide=True)

intersect = calculate_intersection_point(ball, time_to_ball)
desired_ball_direction = opponent.goal_coords - intersect
# TODO: factor in deceleration to ball.velocity
desired_impact_direction = desired_ball_direction - ball.velocity 
desired_ball_impact_speed = desired_impact_direction.length()
# account for ball radius
required_impact_angle = desired_impact_direction.ground_direction() + math.pi
intersect.x += BALL_RADIUS * math.sin(required_impact_angle)
intersect.z += BALL_RADIUS * math.cos(required_impact_angle)
# we probably want to translate intersect to (car - closest_edge/corner)
# how to factor in car.forward?
ball_intersection_point = intersect
optimal_boost = boost_tracker.find_optimal_boost()
