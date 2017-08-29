from tkinter import *
import QuadratBot
import copy

def time_to_ball_impact(car):
    # stuff

def y(t):
    g = 13 # m/s^2 
    return ball.position.y - BALL_RADIUS + ball.velocity.y * t - g * t**2 / 2

def x(t):
    return ball.position.x + ball.velocity.x * 0.97**t

def z(t):
    return ball.position.z + ball.velocity.z * 0.97**t


class display:
    canvas_width = 240
    canvas_height = 164
    master = Tk()
    master.call('wm', 'attributes', '.', '-topmost', '1')
    w = Canvas(master, width=canvas_width, height=canvas_height + 200)
    w.pack()

    def run(self, data):
        canvas_width = self.canvas_width
        canvas_height = self.canvas_height

        player1 = copy.deepcopy(data[0])
        player1.Pos.x = int(player1.Pos.x + canvas_width / 2)
        player1.Pos.y = int(-player1.Pos.y + canvas_height / 2)

        ball =  copy.deepcopy(data[1])
        f_pos = ball.TrajectoryPos(2)
        f_pos.x = int(f_pos.x + canvas_width / 2)
        f_pos.y = int(-f_pos.y + canvas_height / 2)
        ball.Pos.x = int(ball.Pos.x + canvas_width / 2)
        ball.Pos.y = int(-ball.Pos.y + canvas_height / 2)
        
        intersect =  copy.deepcopy(data[2])
        intersect.x = int(intersect.x + canvas_width / 2)
        intersect.y = int(-intersect.y + canvas_height / 2)
        
        trajectory = copy.deepcopy(data[3])
        
        master = self.master
        w = self.w


        w.delete("all")
        w.create_rectangle(0, 0, canvas_width, canvas_height, fill="lightgreen")

        i = 0
        for pos in trajectory:
            pos.x = int(pos.x + canvas_width / 2)
            pos.y = int(-pos.y + canvas_height / 2)
            color = "green"
            if(pos.z <= QuadratBot.BALL_RADIUS):
                color = "red"
            w.create_rectangle(pos.x, pos.y, pos.x + 1, pos.y + 1,
                               outline=color)
            z = canvas_height + 200 - int(200 * pos.z / QuadratBot.FIELD_HEIGHT)
            w.create_rectangle(int(i), z, int(i) + 1, z,
                               outline=color)
            i += canvas_width / len(trajectory)

        w.create_rectangle(player1.Pos.x - 1, player1.Pos.y - 1, player1.Pos.x + 1, player1.Pos.y + 1, fill="blue",
                           outline="blue")
        w.create_line(ball.Pos.x, ball.Pos.y, f_pos.x, f_pos.y, fill="grey")
        w.create_rectangle(ball.Pos.x - 1, ball.Pos.y - 1, ball.Pos.x + 1, ball.Pos.y + 1, fill="white",
                           outline="white")

        w.create_rectangle(intersect.x - 1, intersect.y - 1, intersect.x + 1, intersect.y + 1, fill="black",
                           outline="black")

        master.update_idletasks()
        master.update()