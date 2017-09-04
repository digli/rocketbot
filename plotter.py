from constants import *
from ball import Ball
import matplotlib.pyplot as plt

ball = Ball()
ball.velocity.set(60, 7, 40)
ball.position.set(60, BALL_RADIUS, 30)
path = ball.predict_path(5/60)

x = [b.position.x for b in path]
z = [b.position.z for b in path]
y = [b.position.y for b in path]

plt.figure(1)
plt.plot(z, x, 'o')
plt.figure(2)
plt.plot(y, 'o')

plt.show()
