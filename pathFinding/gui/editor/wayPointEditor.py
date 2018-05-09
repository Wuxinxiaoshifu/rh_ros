import Tkinter as tk
from engine.geometry import calcs
from gui import Drawable, draw
from gui.draw import DEFAULT_COLOR, DEFAULT_POINT_SIZE
import numpy as np
from subGUI import SubGUI


class WayPointEditor(SubGUI, Drawable):

    def __init__(self, radius=DEFAULT_POINT_SIZE, color=DEFAULT_COLOR):
        self._points = []
        self._startVelocity = None
        self._radius = radius
        self._color = color
        self._offset = None
        self._dragIndex = None

    def onSwitch(self, debugInput):
        SubGUI.onSwitch(self, debugInput)
        self._points = [debugInput.scenario.startPoint]
        self._startVelocity = debugInput.scenario.startVelocity
        self._points.extend(debugInput.scenario.wayPoints)
    
    def sync(self):
        self._debugInput.scenario.startPoint = self._points[0]
        self._debugInput.scenario.startVelocity = self._startVelocity
        if len(self._points) > 1:
            self._debugInput.scenario.wayPoints = self._points[1:]
    
    def onLeftPress(self, point, control=False):
        if control:
            if len(self._points) > 0:
                (trash, self._dragIndex) = calcs.findClosestPoint(point, self._points)
                self._offset = self._points[self._dragIndex] - point
        self.sync()

    def onLeftRelease(self, point, control=False):
        if control:
            self._dragIndex = None
        else:
            self._points.append(point)
        self.sync()

    def onMotion(self, point, control=False):
        if control:
            if self._dragIndex is not None:
                self._points[self._dragIndex] = point + self._offset
        self.sync()

    def onKey(self, point, key, ctrl=False):
        if key == "v":
            self._startVelocity = point - self._points[0]
        if key == "Delete":
            if len(self._points) > 1:
                (distance, index) = calcs.findClosestPoint(point, self._points)
                self._points.pop(index)
        self.sync()

    def draw(self, canvas, **kwargs):
        pass
