from engine.interface.fileUtils import SCENARIO_KEY
from gui import draw
from gui.core import Drawable


class SubGUI(Drawable):
    """Depending on mode of GeometryCreator, a subGUI will be signalled to take action in response to input events."""

    def __init__(self):
        self._inputDict = None

    def onLeftPress(self, point, control=False):
        pass

    def onLeftRelease(self, point, control=False):
        pass

    def onMotion(self, point, control=False):
        pass

    def onKey(self, point, key, ctrl=False):
        pass

    def onSwitch(self, params, scenario, vehicle, testInput, visualizer):
        self._params = params
        self._scenario = scenario
        self._vehicle = vehicle
        self._testInput = testInput
        self._visualizer = visualizer

    def onExit(self):
        pass
    
    def draw(self, visualizer, **kwargs):
        draw.drawScenario(visualizer, self._scenario)
