from tkinter import *
from constants import *
from ball import Ball
import copy
import matplotlib.pyplot as plt


class display:
    canvas_width = 240
    canvas_height = 164
    master = Tk()
    master.call('wm', 'attributes', '.', '-topmost', '1')
    w = Canvas(master, width=canvas_width, height=canvas_height + 200)
    w.pack()

    def run(self, trajectory):
        canvas_width = self.canvas_width
        canvas_height = self.canvas_height
        master = self.master
        w = self.w
        w.delete("all")
        w.create_rectangle(0, 0, canvas_width, canvas_height, fill="lightgreen")

        i = 0
        for mock in trajectory:
            pos = mock.position
            pos.x = int(pos.x + canvas_width / 2)
            pos.y = int(-pos.y + canvas_height / 2)
            color = "green"
            if(pos.z <= BALL_RADIUS):
                color = "red"
            w.create_rectangle(pos.x, pos.y, pos.x + 1, pos.y + 1, outline=color)
            z = canvas_height + 200 - int(200 * pos.z / FIELD_HEIGHT)
            w.create_rectangle(int(i), z, int(i) + 1, z, outline=color)
            i += canvas_width / len(trajectory)

        master.update_idletasks()
        master.update()

if __name__ == '__main__':
    ball = Ball()
    ball.velocity.set(10, 0, 20)
    ball.position.set(0, BALL_RADIUS, 0)
    display().run(ball.predict_path(2/60))

