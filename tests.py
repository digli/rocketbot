from constants import *
from utils import *
from car import *
from ball import *
import unittest

blue = Blue()
orange = Orange()
ball = Ball()

class TestBall(unittest.TestCase):

    def test_going_into_goal(self):
        ball.position.set(0, 0, 0)
        ball.velocity.set(1, 0, 1)
        ball.update()
        self.assertFalse(ball.going_into_goal(blue))
        self.assertFalse(ball.going_into_goal(orange))
        ball.position.set(-10, 0, FIELD_HALF_Z - 10)
        ball.update()
        self.assertFalse(ball.going_into_goal(blue))
        self.assertTrue(ball.going_into_goal(orange))
        ball.velocity.set(0, 0, -1)
        ball.update()
        self.assertTrue(ball.going_into_goal(blue))
        self.assertFalse(ball.going_into_goal(orange))

class TestCar(unittest.TestCase):

    def test_arc_prediction(self):
        car = Car()
        car.velocity.set(3, 0, 10)
        car.speed = car.velocity.length()
        car.forward = car.velocity.ground_direction()
        left = car.left_arc_mock()
        right = car.right_arc_mock()
        straight = car.straight_forward_mock()
        self.assertTrue(left.position.x > straight.position.x > right.position.x)
        self.assertTrue(left.forward > straight.forward > right.forward)

    def test_dodge_mock(self):
        car = Car()
        car.velocity.set(10, 0, 20)
        car.speed = car.velocity.length()
        car.forward = math.atan2(car.velocity.x, car.velocity.z)
        mock = car.dodge_mock()
        mock.speed = mock.velocity.length()
        mock.forward = math.atan2(mock.velocity.x, mock.velocity.z)
        self.assertTrue(9.99 < mock.speed - car.speed < 10.01)
        self.assertTrue(abs(car.forward - mock.forward) < 0.001)
        for i in range(5):
            mock = mock.dodge_mock()
        self.assertTrue(abs(mock.velocity.length() - CAR_MAX_SPEED < 0.1))

if __name__ == '__main__':
    unittest.main()

