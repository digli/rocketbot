
YAW_SENSITIVITY = 7
POWERSLIDE_THRESHOLD = 1.8 # Radians
STICK_MAX = 32767
STICK_MIDDLE = 16383
STICK_MIN = 0
STICK_LEFT = STICK_MIN
STICK_RIGHT = STICK_MAX

FIELD_HALF_Z = 102.4
FIELD_HALF_X = 81.92
FIELD_HEIGHT = 40
# goal_width = 22% of full_field_x,  Derived from pixel measurements ^))
GOAL_HALF_WIDTH = HALF_SIZE_X * 0.22 
GOAL_POST_TOP_X = GOAL_HALF_WIDTH
GOAL_POST_BOT_X = -GOAL_HALF_WIDTH
# Dave mentions that goal would be over 24.5 meters with a conversin rate of 3.653
# https://www.reddit.com/r/RocketLeague/comments/3b00fn/rocket_league_physics_and_field_size/cshs8w1/
GOAL_HEIGHT = 6.71

BALL_RADIUS = 1.8555

# not 100% accurate
BOOST_MIDFIELD_X = 71
BOOST_CORNER_X = 62
BOOST_CORNER_Z = 81
BOOST_RADIUS_SQUARED = 16 # idk, test this number

# https://docs.google.com/spreadsheets/d/1A6jBshi5szfjIiPFmTbJXzBxtVhxEHPjmKC0xcSCUGk/edit#gid=1536046193
OCTANE_LENGTH = 1.180074
OCTANE_WIDTH = 0.8419941
OCTANE_HEIGHT = 0.3615907
OCTANE_ELEVATION = 0.2075499
OCTANE_NET_HEIGHT = 0.3883453
OCTANE_HITBOX_OFFSET = 0.1387566
OCTANE_PIVOT_PT_TO_FRONT = 0.7287936

GRAVITY_CONSTANT = 6.5 # m/s^2
# perhaps 23 is without boost, 51.4 is with boost
CAR_MAX_SPEED = 23 # m/s (can't be correct) 51.4 sounds more like it

JUMP_TO_DODGE_DT = 0.3 # (seconds) __test this__
DODGE_TIME_LIMIT = 2 # (seconds) according to random guide on steam