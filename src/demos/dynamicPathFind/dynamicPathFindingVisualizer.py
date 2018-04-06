import copy

from dynamicPathFinderDrawable import DynamicPathFinderDrawable
from gui.visualizer import Visualizer

# TODO: Not currently used
SNAP_PIXEL_DISTANCE = 10
STEPS_PER_CLICK = 1


class DynamicPathFindingVisualizer(Visualizer):
    """
    Visualizes the dynamic path finding process.
    """

    def __init__(self, dynamicPathFinder, *args, **kwargs):
        Visualizer.__init__(self, *args, **kwargs)
        self._resetDynamicPathFinder = dynamicPathFinder
        self._dynamicPathFinder = copy.deepcopy(self._resetDynamicPathFinder)
        self.pointOfInterest = None

    def onLeftClick(self, event):
        for i in range(0, STEPS_PER_CLICK):
            self.doRealStep()
        self.updateDisplay()

    def doRealStep(self):
        while not self._dynamicPathFinder.isDone() and not self._dynamicPathFinder.step():
            pass

    def onMouseMotion(self, event):
        self.pointOfInterest = self.transformCanvasToPoint((event.x, event.y))
        self.updateDisplay()

    def onRightClick(self, event):
        self._dynamicPathFinder = copy.deepcopy(self._resetDynamicPathFinder)
        self.updateDisplay()

    def updateDisplay(self):
        drawable = DynamicPathFinderDrawable(self._dynamicPathFinder)
        self.drawToCanvas(drawable, pointOfInterest=self.pointOfInterest, snapDistance=5.0)
