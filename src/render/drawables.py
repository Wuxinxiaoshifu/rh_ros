from Tkinter import Canvas

import numpy as np

from render.Drawable import Drawable


class DrawableLine(dict, Drawable):
    """Used to hold information about a line to draw on a canvas.
    It holds the coordinates of the line and is also a dictionary passed to the create_line() method."""

    def __init__(self, x1=None, y1=None, x2=None, y2=None, lineString=None, text=None, **kwargs):
        dict.__init__(self, **kwargs)
        self.text = text
        if lineString is None:
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
        else:
            self.x1 = float(lineString.coords[0][0])
            self.y1 = float(lineString.coords[0][1])
            self.x2 = float(lineString.coords[1][0])
            self.y2 = float(lineString.coords[1][1])

    def draw(self, canvas):
        # type: (Canvas)->None

        midPoint = np.array([(self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2])
        textOffset = np.array([-self.y2 - self.y1, self.x2 - self.x1])
        textOffset = 4 * textOffset / np.linalg.norm(textOffset, 2)
        textPos = midPoint + textOffset
        canvas.create_text(textPos[0], textPos[1], text=self.text, fill="black")
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, **self)


class DrawableCircle(dict, Drawable):
    """Used to hold information about a circle to draw on a canvas.
    It holds the coordinates of the circle and is also a dictionary passed to the create_oval() method."""

    def __init__(self, x=None, y=None, radius=None, **kwargs):
        dict.__init__(self, **kwargs)
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, canvas):
        # type: (Canvas)->None
        canvas.create_oval(self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius,
                           **self)


class DrawablePolygon(dict, Drawable):
    def __init__(self, points, **kwargs):
        dict.__init__(self, **kwargs)
        self.points = points

    def draw(self, canvas):
        # type: (Canvas)->None
        coords = []
        for point in self.points:
            coords.append(point[0])
            coords.append(point[1])
        canvas.create_polygon(coords, **self)
