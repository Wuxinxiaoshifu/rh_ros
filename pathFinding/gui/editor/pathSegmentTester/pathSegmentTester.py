import Tkinter as tk
from engine.interface.fileUtils import TEST_INPUT_KEY, SCENARIO_KEY
from gui import Drawable, draw
from gui.draw import DEFAULT_COLOR, DEFAULT_POINT_SIZE
from gui.editor.subGUI import SubGUI
from obstacleDebug import ObstacleCourseDebug


class PathSegmentTester(Drawable, SubGUI):

    def __init__(self, obstacleData):
        self._obstacleData = obstacleData
        self._pointOfInterest = None
        self._obstacleDebug = None
        self._showPathsToPoints = False
        self._pathSegments = []
        self._filteredPathSegments = []

    def onLeftRelease(self, point, control=False):
        if control:
            self._inputDict[TEST_INPUT_KEY].targetPoint = point
        else:
            self._inputDict[TEST_INPUT_KEY].startPoint = point

    def onKey(self, point, key, ctrl=False):
        if key == "v":
            if ctrl:
                self._inputDict[TEST_INPUT_KEY].velocityOfTarget = point - self._inputDict[TEST_INPUT_KEY].targetPoint
            else:
                self._inputDict[TEST_INPUT_KEY].startVelocity = point - self._inputDict[TEST_INPUT_KEY].startPoint

        if key == "z":
            self._showPathsToPoints = not self._showPathsToPoints

    def onMotion(self, point, control=False):
        self._pointOfInterest = point

    def onSwitch(self, debugInput):
        SubGUI.onSwitch(self, debugInput)
        self._obstacleDebug = ObstacleCourseDebug(self._inputDict[SCENARIO_KEY].boundaryPoints,
                                                  self._inputDict[SCENARIO_KEY].noFlyZones)
        self._obstacleData.setInitialState(self._inputDict[SCENARIO_KEY].boundaryPoints,
                                                  self._inputDict[SCENARIO_KEY].noFlyZones)

    def draw(self, canvas, radius=DEFAULT_POINT_SIZE, color=DEFAULT_COLOR, **kwargs):
        draw.drawPoint(canvas, self._inputDict[TEST_INPUT_KEY].startPoint, radius=radius, color=color)
        draw.drawLine(canvas, self._inputDict[TEST_INPUT_KEY].startPoint,
                      self._inputDict[TEST_INPUT_KEY].startPoint + self._inputDict[TEST_INPUT_KEY].startVelocity,
                      arrow=tk.LAST)

        goalSegment = self._obstacleData.findPathSegment(startTime=0.0,
                                                         startPoint=self._inputDict[TEST_INPUT_KEY].startPoint,
                                                         startVelocity=self._inputDict[TEST_INPUT_KEY].startVelocity,
                                                         targetPoint=self._inputDict[TEST_INPUT_KEY].targetPoint,
                                                         velocityOfTarget=self._inputDict[TEST_INPUT_KEY].velocityOfTarget)

        # Draw obstacles as they appear at this time
        drawTime = 0.0
        if goalSegment is not None:
            goalSegment.draw(canvas)

            if self._pointOfInterest is not None:
                (closestPoint, distance, pointTime) = goalSegment.calcPointDebug(self._pointOfInterest)
                if distance < 2.0:
                    drawTime = pointTime
                    draw.drawPoint(canvas, closestPoint, radius=radius, color="orange")
                    self._obstacleDebug.draw(canvas, time=drawTime, boundaryColor="red", nfzColor="blue")

        if self._showPathsToPoints:
            (self._pathSegments, self._filteredPathSegments) = self._obstacleData.findPathSegments(startTime=0.0,
                                                                                                   startPoint=self._inputDict[TEST_INPUT_KEY].startPoint,
                                                                                                   startVelocity=self._inputDict[TEST_INPUT_KEY].startVelocity)
        else:
            self._pathSegments = []
            self._filteredPathSegments = []

        for pathSegment in self._pathSegments:
            pathSegment.draw(canvas)
        for pathSegment in self._filteredPathSegments:
            pathSegment.draw(canvas, filtered=True)

        targetPoint = self._inputDict[TEST_INPUT_KEY].targetPoint + self._inputDict[TEST_INPUT_KEY].velocityOfTarget * drawTime
        draw.drawPoint(canvas, targetPoint, radius=radius, color=color)
        draw.drawLine(canvas, targetPoint,
                      targetPoint + self._inputDict[TEST_INPUT_KEY].velocityOfTarget,
                      arrow=tk.LAST)
