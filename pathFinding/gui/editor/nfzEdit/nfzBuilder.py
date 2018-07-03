from engine.interface.fileUtils import SCENARIO_KEY
from engine.interface.noFlyZone import NoFlyZone
from gui import Drawable
from gui.editor.polyBuilder import PolyBuilder


class NFZBuilder(PolyBuilder, Drawable):

    def __init__(self):
        PolyBuilder.__init__(self)

    def _polyBuilt(self, points):
        self._inputDict[SCENARIO_KEY].noFlyZones.append(NoFlyZone(points, (0.0, 0.0)))

