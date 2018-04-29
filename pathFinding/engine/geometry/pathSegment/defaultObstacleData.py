import math

import numpy as np
from typing import Sequence, List

from engine.geometry import calcs, PathSegment
from engine.geometry.pathSegment.defaultPathSegment import DefaultPathSegment
from engine.geometry.pathSegment.obstacleLineSegment import ObstacleLineSegment
from obstacleData import ObstacleData


class DefaultObstacleData(ObstacleData):
    """
    A base class for Python implementations of ObstacleData.  Sub-classes should implement the following:
    createPathSegment() -- Create path segments from starting position to ending position
    filterImpossiblePathSegments() -- Filter out path segments which intersect the boundary or NoFlyZones.
    """

    def __init__(self, targetOffsetLength):
        # Initial position of no fly zone vertices, plus any offsetting at time=0.0.
        self.targetPoints = []

        # Velocity of the target points (corresponding to the NFZ they belong to).
        self.targetVelocities = []
        self.targetPointNormals = []
        self.targetCosLimits = []

        self.obstacleLines = []

        # A version of the target points at the current query time.  These are actually used to compute potential path
        # segments
        self.targetPointsAtTime = []

        # A version of the obstacle lines blocking potential paths to the targets at the current query time
        self.obstacleLinesAtTime = []

        # When finding paths to no fly zone vertices, this applies an "outward" offset to each vertex of this length
        self.targetOffsetLength = targetOffsetLength

    def setInitialState(self, initialPathFindingInput):
        del self.targetPoints[:]
        del self.targetPointNormals[:]
        del self.targetCosLimits[:]
        del self.targetVelocities[:]
        del self.obstacleLines[:]

        for noFlyZoneInput in initialPathFindingInput.noFlyZones:
            points = noFlyZoneInput.points
            nfzLines = []
            for i in range(0, len(points)):
                nfzLines.append(
                    ObstacleLineSegment(points[i - 1], points[i], np.array(noFlyZoneInput.velocity, np.double)))

            for i in range(-1, len(points) - 1):
                pointNormal = (nfzLines[i].n + nfzLines[i + 1].n) / 2.0
                pointNormal /= np.linalg.norm(pointNormal)
                # Angle between adjacent edges should mostly be large (>180) given winding direction
                pointAngle = calcs.calcEdgeAngle(points[i - 1], points[i], points[i + 1])
                if pointAngle > math.pi:
                    cosLimit = math.cos(pointAngle / 2.0)
                else:
                    cosLimit = 1

                self.targetPointNormals.append(pointNormal)
                self.targetCosLimits.append(cosLimit)
                self.targetPoints.append(nfzLines[i].p2 + pointNormal * self.targetOffsetLength)
                self.targetVelocities.append(np.array(noFlyZoneInput.velocity, np.double))

            self.obstacleLines.extend(nfzLines)

        for i in range(len(initialPathFindingInput.boundaryPoints)):
            self.obstacleLines.append(
                ObstacleLineSegment(initialPathFindingInput.boundaryPoints[i - 1],
                                    initialPathFindingInput.boundaryPoints[i], np.array((0, 0), np.double)))

        # Create copy of same length corresponding to time = 0.0
        self.targetPointsAtTime = self.targetPoints[:]
        self.obstacleLinesAtTime = self.obstacleLines[:]

    def setQueryTime(self, time):
        for i in range(len(self.targetPoints)):
            self.targetPointsAtTime[i] = self.targetPoints[i] + self.targetVelocities[i] * time

        for i in range(len(self.obstacleLines)):
            offset = self.obstacleLines[i].velocity * time
            self.obstacleLinesAtTime[i] = ObstacleLineSegment(self.obstacleLines[i].p1 + offset,
                                                              self.obstacleLines[i].p2 + offset,
                                                              self.obstacleLines[i].velocity)

    def findPathSegment(self, startPoint, startVelocity, targetPoint, velocityOfTarget):
        pathSegment = self.createPathSegment(startPoint, startVelocity, targetPoint, velocityOfTarget)

        if pathSegment is not None and self.filterPathSegment(pathSegment, self.obstacleLinesAtTime):
            return pathSegment
        else:
            return None

    def findPathSegments(self, startPoint, startVelocity):
        # type: (Sequence,Sequence)->[PathSegment]

        rawPathSegments = []  # type: List[DefaultPathSegment]
        filteredPathSegments = []  # type: List[DefaultPathSegment]
        for i in range(len(self.targetPoints)):
            velocityOfTarget = self.targetVelocities[i]
            targetPoint = self.targetPointsAtTime[i]

            # startPosition will typically be a NFZ vertex.  We want to eliminate search from a start position to itself.
            if not calcs.arePointsClose(startPoint, targetPoint):
                pathSegment = self.createPathSegment(startPoint, startVelocity, targetPoint, velocityOfTarget)
                if pathSegment is not None:
                    # Filter path segment based on incoming angle and known geometry around point.
                    pointNormal = self.targetPointNormals[i]
                    cosLimit = self.targetCosLimits[i]
                    relativeVelocity = pathSegment.endVelocity - velocityOfTarget
                    relativeVelocity /= np.linalg.norm((relativeVelocity))
                    if np.dot(relativeVelocity, pointNormal) >= cosLimit:
                        rawPathSegments.append(pathSegment)
                    else:
                        filteredPathSegments.append(pathSegment)

        pathSegments = []

        for pathSegment in rawPathSegments:
            if self.filterPathSegment(pathSegment, self.obstacleLinesAtTime):
                pathSegments.append(pathSegment)
            else:
                filteredPathSegments.append(pathSegment)
        return (pathSegments, filteredPathSegments)

    def createPathSegment(self, startPoint, startVelocity, targetPoint, velocityOfTarget):
        # type: () -> DefaultPathSegment
        """
        Creates a PathSegment object from the given start point and velocity, which will hit the target, which is moving
        at a given velocity.
        :param startPoint:
        :param startVelocity:
        :param targetPoint:
        :param velocityOfTarget:
        :return:
        """
        pass

    def filterPathSegment(self, pathSegment, obstacleLines):
        for i in range(len(obstacleLines)):
            obstacleLine = obstacleLines[i]
            if pathSegment.intersectsLine(obstacleLine):
                return False
        return True
