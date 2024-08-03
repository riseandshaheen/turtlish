import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from PIL import Image
from io import BytesIO
import base64
import re

class Turtlish:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-250, 250)
        self.ax.set_ylim(-250, 250)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

        self.current_position = (0,0)
        self.current_angle = 0
        self.heading = 0.0
        self.pen = True
        self.color = 'black'
        self.width = 0.7

    def _update_position(self, new_position):
        if self.pen:
            self.ax.plot(
                [self.current_position[0], new_position[0]],
                [self.current_position[1], new_position[1]],
                color=self.color,
                linewidth=self.width
            )
        self.current_position = new_position

    def forward(self, distance):
        rad = np.radians(self.current_angle)
        new_position = (
            self.current_position[0] + distance * np.cos(rad),
            self.current_position[1] + distance * np.sin(rad)
        )
        self._update_position(new_position)

    def fd(self, distance):
        self.forward(distance)

    def backward(self, distance):
        self.forward(-distance)
    
    def bk(self, distance):
        self.backward(distance)
    
    def back(self, distance):
        self.backward(distance)

    def right(self, angle):
        self.current_angle -= angle
    
    def rt(self, angle):
        self.right(angle)

    def left(self, angle):
        self.current_angle += angle
    
    def lt(self, angle):
        self.left(angle)

    def penup(self):
        self.pen = False

    def pendown(self):
        self.pen = True
    
    def pensize(self, width):
        self.width = width

    def circle(self, radius, extent=None, steps=None):
        if steps is None:
            steps = int(abs(radius) * np.pi / 10) 
        if extent is None:
            extent = 360

        angle_step = float(extent) / steps
        step_length = 2 * np.pi * abs(radius) * abs(angle_step) / 360

        for _ in range(steps):
            self.forward(step_length)
            self.left(angle_step)

    def dot(self, size=6, color='black'):
        self.ax.plot(self.current_position[0], self.current_position[1], 'o', markersize=size, color=color)
    
    def color(self, color):
        self.color = color

    def begin_fill(self):
        self.fill = True
        self.path = []

    def end_fill(self):
        if self.fill:
            self.path.append(self.position.copy())
            polygon = mlines.Line2D(*zip(*self.path), color='black', linestyle='-', linewidth=1)
            self.ax.add_line(polygon)
            self.fill = False
            self.path = []

    def goto(self, x, y):
        self._update_position((x, y))
    
    def setx(self, x):
        self.goto(x, self.current_position[1])

    def sety(self, y):
        self.goto(self.current_position[0], y)

    def setheading(self, angle):
        self.heading = angle

    def home(self):
        self.goto(0, 0)
        self.setheading(0)
    
    def get_figure_and_ax(self):
        return self.fig, self.ax

def find_turtle_instance(code):
    # Look for a line that defines a MatplotlibTurtle instance
    match = re.search(r'(\w+)\s*=\s*Turtlish\(\)', code)
    if match:
        return match.group(1)
    return None

def draw_with_turtle_to_base64(code):

    # Check if the code includes MatplotlibTurtle initialization
    if find_turtle_instance(code) is None:
        raise ValueError("No Turtlish instance found in the provided code.")

    exec(code, globals())

    # find the instance of Turtlish from global variables
    turtle_instance = next(
        (obj for obj in globals().values() if isinstance(obj, Turtlish)),
        None
    )

    if turtle_instance is None:
        raise ValueError("No Turtlish instance found in the provided code.")

    fig, ax = turtle_instance.get_figure_and_ax()

    # save the figure to a BytesIO object
    buf = BytesIO()
    fig.canvas.print_png(buf)
    buf.seek(0)
    img = Image.open(buf)

    with BytesIO() as output:
        img.save(output, format='PNG')
        base64_img = base64.b64encode(output.getvalue()).decode('utf-8')

    return base64_img
