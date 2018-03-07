import Tkinter as tk
from Tkinter import Canvas

root = tk.Tk()
root.withdraw()


def startGUI():
    root.mainloop()


def inGUIThread(task, *args):
    """Run a task in the GUI thread"""
    root.after_idle(task, *args)


class Drawable:
    """Something that can be draw itself on the given TK Canvas object."""

    def draw(self, canvas, **kwargs):
        """
        Draw on the canvas with any modifiers stored in kwargs.
        :param canvas:
        :param kwargs:
        :return:
        """
        # type: (Canvas) -> None
        pass


class DrawListener:
    """Used for computations threads that want to communicate back to the GUI, on a regular basis, with a new state to draw."""

    def onDraw(self, drawable, **kwargs):
        pass
