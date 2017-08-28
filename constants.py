import math

YAW_SENSITIVITY = 7
DODGE_SENSITIVITY = 3
KICKOFF_YAW_SENSITIVITY = 8
POWERSLIDE_THRESHOLD = 1.6 # Radians (REMEMBER TO TRY SMALLER VALUES)
STICK_MAX = 32767
STICK_MIDDLE = 16383
STICK_MIN = 0

FIELD_HALF_Z = 102.4
FIELD_HALF_X = 81.92
FIELD_HEIGHT = 40
# goal_width = 22% of full_field_x,  Derived from pixel measurements ^))
GOAL_HALF_WIDTH = FIELD_HALF_X * 0.22 
GOAL_POST_TOP_X = GOAL_HALF_WIDTH
GOAL_POST_BOT_X = -GOAL_HALF_WIDTH
# Dave mentions that goal would be over 24.5 meters with a conversion rate of 3.653
# https://www.reddit.com/r/RocketLeague/comments/3b00fn/rocket_league_physics_and_field_size/cshs8w1/
GOAL_HEIGHT = 13.41

BALL_RADIUS = 1.83555

# not 100% accurate
BOOST_MIDFIELD_X = 71
BOOST_CORNER_X = 62
BOOST_CORNER_Z = 81
BIG_BOOST_RADIUS_SQUARED = 16 # idk, test this number
BIG_BOOST_RESPAWN_TIME = 10
SMALL_BOOST_RADIUS_SQUARED = 4 # idk, test this number
SMALL_BOOST_RESPAWN_TIME = 5 # idk, test this number

# https://docs.google.com/spreadsheets/d/1A6jBshi5szfjIiPFmTbJXzBxtVhxEHPjmKC0xcSCUGk/edit#gid=1536046193
# Are these unreal units? probably.
OCTANE_LENGTH = 1.180074
OCTANE_WIDTH = 0.8419941
OCTANE_HEIGHT = 0.3615907
OCTANE_ELEVATION = 0.2075499
OCTANE_NET_HEIGHT = 0.3883453
OCTANE_HITBOX_OFFSET = 0.1387566
OCTANE_PIVOT_PT_TO_FRONT = 0.7287936

CAR_HEIGHT_THRESHOLD = 0.35

# could possibly be OCTANE_PIVOT_PT_TO_FRONT instead of length but who knows
ANGLE_TO_BUMPER = math.atan(OCTANE_LENGTH / OCTANE_WIDTH)
OCTANE_MID_TO_CORNER = math.hypot(OCTANE_LENGTH, OCTANE_WIDTH)

ANGLE_TO_BUMPER = math.atan(OCTANE_PIVOT_PT_TO_FRONT / OCTANE_WIDTH / 2)
OCTANE_MID_TO_CORNER = math.hypot(OCTANE_PIVOT_PT_TO_FRONT, OCTANE_WIDTH / 2)

# GRAVITY_CONSTANT = 6.5 # this is 6500 uu/s^2. Our conversion rate is 0.02
GRAVITY_CONSTANT = 13 # m/s^2

CAR_MAX_SPEED = 46 # m/s
CAR_SUPERSONIC_THRESHOLD = CAR_MAX_SPEED - 2 # change if needed
CAR_FORCE = 2 # ?

DODGE_TIME_LIMIT = 2 # (seconds) according to random guide on steam
MIN_DODGE_SPEED = 20 # try this out too, could be 20 or smth
MAX_DODGE_SPEED = CAR_MAX_SPEED - 6

################# DodgeTimer #################
JUMP_STARTING = 0
JUMP_BUFFERING = 1
JUMP_DODGING = 2
JUMP_FINISHED = 3
JUMP_TO_DODGE_DT = 0.06 # (seconds) __test this__
FULL_DODGE_DURATION = 1.6
UPDATE_BUFFER = 1 / 60
DODGE_SPEED_INCREMENT = 10
