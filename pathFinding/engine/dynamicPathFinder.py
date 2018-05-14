import time

from constants import NO_FLY_ZONE_POINT_OFFSET
from engine.geometry.pathSegment.arcObstacleData import ArcObstacleData
from engine.geometry.pathSegment.lineSegmentObstacleData import LineSegmentObstacleData
from engine.vertex import UniqueVertexQueue
from engine.vertex.vertexPriorityQueue import QueueEmptyException
from geometry import calcs
import numpy as np
from vertex import Vertex


class DynamicPathFinder:

    def __init__(self, scenario, vehicle):

        self._obstacleData = ArcObstacleData(vehicle.acceleration)
#         self._obstacleData = LineSegmentObstacleData(NO_FLY_ZONE_POINT_OFFSET)
        self._obstacleData.setInitialState(scenario.boundaryPoints, scenario.noFlyZones)

        # Calculate bounding rectangle and use that for dimensions of the UniqueVertexQueue
        bounds = scenario.calcBounds()
        self._vertexQueue = UniqueVertexQueue(bounds[0], bounds[1], bounds[2], bounds[3], vehicle.maxSpeed)

        self._start = np.array(scenario.startPoint, np.double)
        self._goal = np.array(scenario.wayPoints[0], np.double)
        velocity = np.array(scenario.startVelocity, np.double)
        self._currentVertex = Vertex(position=self._start,
                                     velocity=velocity,
                                     timeToVertex=0.0,
                                     estimatedTimeThroughVertex=self.heuristic(self._start, velocity))

        self._pathSegments = []
        self._filteredPathSegments = []
        self._solution = None
        self._bestSolutionTime = float("inf")

        self._vertexQueue.push(self._currentVertex)
        self._numQueuedVertices = 1
        self._computeTime = 0.0
        self._findPathsTime = 0.0
        self._queueComputeTime = 0.0

    def findPath(self):
        while not self.isDone():
            self.step()

    def isDone(self):
        return self._vertexQueue.isEmpty()
    
    def step(self):
        try:
            self._currentVertex = self._vertexQueue.pop()
            while self._currentVertex.estimatedTimeThroughVertex > self._bestSolutionTime:
                self._currentVertex = self._vertexQueue.pop()
            
            if self.checkPathToGoal():
                return True
            else:
                self._findPathsTime -= time.time()
                (self._pathSegments, self._filteredPathSegments) = self._obstacleData.findPathSegments(
                    startTime=self._currentVertex.timeToVertex,
                    startPoint=self._currentVertex.position,
                    startVelocity=self._currentVertex.velocity)
                self._findPathsTime += time.time()
                for pathSegment in self._pathSegments:
                    timeToVertex = self._currentVertex.timeToVertex + pathSegment.elapsedTime
        
                    newVertex = Vertex(position=pathSegment.endPoint,
                                       velocity=pathSegment.endVelocity,
                                       timeToVertex=timeToVertex,
                                       estimatedTimeThroughVertex=timeToVertex + self.heuristic(pathSegment.endPoint,
                                                                                                pathSegment.endVelocity),
                                       previousVertex=self._currentVertex,
                                       pathSegment=pathSegment)
        
                    self._vertexQueue.push(newVertex)
                return False
        except QueueEmptyException:
            return True

    def checkPathToGoal(self):
        """
        Check if there is a path from self._currentVertex to the goal.  Update the best solution if this is better.
        :return:
        """
        pathSegment = self._obstacleData.findPathSegment(startTime=self._currentVertex.timeToVertex,
                                                         startPoint=self._currentVertex.position,
                                                         startVelocity=self._currentVertex.velocity,
                                                         targetPoint=self._goal,
                                                         velocityOfTarget=np.array((0, 0), np.double))
        if pathSegment is None:
            return False
        else:
            timeToGoal = self._currentVertex.timeToVertex + pathSegment.elapsedTime
            if timeToGoal < self._bestSolutionTime:
                self._solution = Vertex(position=self._goal,
                                        velocity=pathSegment.endVelocity,
                                        timeToVertex=timeToGoal,
                                        estimatedTimeThroughVertex=timeToGoal,  # timeToVertex + 0
                                        previousVertex=self._currentVertex,
                                        pathSegment=pathSegment)

                self._bestSolutionTime = timeToGoal
            return True
        
    def heuristic(self, point, velocity):
        return calcs.calcTravelTime(point, self._goal, np.linalg.norm(velocity))

    def hasSolution(self):
        return self._solution is not None

    def getSolution(self):
        if self._solution is None:
            return []
        return self.getPathSegments(self._solution)
        
    def getDebugData(self):
        if self._currentVertex is None:
            return ([], [], [])
        previousPathSegments = self.getPathSegments(self._currentVertex)
        return (previousPathSegments, self._pathSegments, self._filteredPathSegments)
        
    def getPathSegments(self, pathEndVertex):
        pathSegments = []
        currentVertex = pathEndVertex
        previousVertex = currentVertex.previousVertex

        while not previousVertex is None:
            pathSegments.append(currentVertex.pathSegment)
            currentVertex = previousVertex
            previousVertex = currentVertex.previousVertex
        return pathSegments        
