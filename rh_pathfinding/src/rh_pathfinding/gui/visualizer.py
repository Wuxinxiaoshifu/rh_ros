from Tkinter import Canvas
from Tkinter import Toplevel
import os

import Tkinter as tk
import core
import numpy as np


class Visualizer(Toplevel, core.DrawListener):
    """
    Base class for windows used for visualization of problems.  Deals with many boilerplate TK tasks and has several features.
    - Registers blank listeners for common events and registers exit on close
    - Provides a "virtual coordinate system" that maps onto the window.  This is specified as a position and a width/height.
    - Provides reverse transform from mouse coordinates back to "virtual coordinate system"
    - Allows posting drawing into the GUI thread.  This can be overwhelmed if submissions are too fast.  This should leverage TK's dirty/repaint scheme in some way in the future.
    """

    def __init__(self, canvasWidth, canvasHeight, viewCenterX=0.0, viewCenterY=0.0, viewWidth=1.0, viewHeight=1.0, **kw):
        Toplevel.__init__(self, **kw)
        self.viewCenterX = viewCenterX
        self.viewCenterY = viewCenterY
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight
        self.canvas = Canvas(self, width=canvasWidth, height=canvasHeight)
        self.canvas.pack()
        self.protocol("WM_DELETE_WINDOW", self.onClose)
        self.bind("<Configure>", self.onResize)

    def setView(self, viewCenterX, viewCenterY, viewWidth, viewHeight):
        self.viewCenterX = viewCenterX
        self.viewCenterY = viewCenterY
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight

    def bindWithTransform(self, eventName, handler):
        """
        Binds non-standard handlers to events.  These handlers receive the initial event object, but also an additional
        point parameter which holds the event's location in the "virtual coordinate system" as a numpy array.
        :param eventName:
        :param handler: a handler function with 2 args (point,event)
        :return:
        """
        self.bind(eventName, lambda event: handler(self.transformCanvasToPoint((event.x, event.y)), event))

    def drawInBackground(self, drawable, **kwargs):
        """Draw the given drawable in the GUI thread.
        drawable should not be touched while drawing."""
        core.inGUIThread(lambda: self.drawToCanvas(drawable, **kwargs))

    def drawToCanvas(self, drawable, **kwargs):
        """Draw the given drawable, applying virtual coordinates transform.
        Must be called from GUI THREAD!"""
        self.canvas.delete(tk.ALL)
        drawable.draw(self, **kwargs)
        self.transformCanvas()

    def transformCanvas(self):
        """Transforms all objects drawn on the canvas in the "virtual coordinate system" to the window's coordinates."""
        canvas = self.canvas
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        canvas.move("all", -self.viewCenterX, -self.viewCenterY)
        canvas.scale("all", 0.0, 0.0, width / self.viewWidth, -height / self.viewHeight)
        canvas.move("all", width / 2.0, height / 2.0)

    def transformCanvasToPoint(self, canvasPoint):
        """
        Given a point on the canvas, such as a mouse coordinate, transform it to the "virtual coordinate system".
        :param canvasPoint: point to transform
        :return: (transX, transY)
        """
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        transX = self.viewCenterX + self.viewWidth * (canvasPoint[0] - width / 2.0) / width
        transY = self.viewCenterY - self.viewHeight * (canvasPoint[1] - height / 2.0) / height
        return np.array((transX, transY), np.double)

    def pixelVecToScale(self, vec):
        """
        Scale the given vector, expressed in pixels, to the transform, currently in use.  This allows, things like offsets and the radius of
        points to always be displayed with the same absolute size on the screen.
        """
        return vec * np.array((self.viewWidth / self.canvas.winfo_width(), self.viewHeight / self.canvas.winfo_height()), np.double)

    def scaleVecToPixels(self, vec):
        return vec * np.array((self.canvas.winfo_width() / self.viewWidth, self.canvas.winfo_height() / self.viewHeight), np.double)

    def onDraw(self, drawable, **kwargs):
        """Callback for DrawListener.  This can be used by a background calculation thread to signal the GUI to draw a new state."""
        self.drawInBackground(drawable)

    def onResize(self, event):
        pass

    def onClose(self):
        os._exit(0)
