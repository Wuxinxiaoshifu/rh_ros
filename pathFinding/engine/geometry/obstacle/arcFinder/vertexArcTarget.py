from engine.geometry import calcs
from engine.geometry.calcs import NoSolutionException
from engine.geometry.obstacle.arcFinder.arcCriticalPoint import ArcCriticalPoint
from engine.geometry.obstacle.arcFinder.arcTarget import ArcTarget
from engine.geometry.obstacle.vertexTarget import VertexTarget
import numpy as np


class VertexArcTarget(VertexTarget, ArcTarget):

    def __init__(self, position, velocity, normal, pointAngle):
        VertexTarget.__init__(self, position, velocity, normal, pointAngle)

    def notInitiallyReachable(self, arc):
        toCenter = self.position - arc.center
        return np.dot(toCenter, toCenter) < arc.radius * arc.radius
    
    def getCriticalPoints(self, arc):
        distances = calcs.getRayCircleIntersections(self.position, self.direction, arc.center, arc.radius)
        criticalPoints = []
        for distance in distances:
            if distance >= 0.0:
                intersectionPoint = self.position + distance * self.direction
                targetTimeToIntersection = distance / self.speed
                
                criticalPoints.append(ArcCriticalPoint(vehicleArc=arc.arcToPoint(intersectionPoint),
                                                       targetArc=targetTimeToIntersection * arc.angularSpeed))
        return criticalPoints

    def iterateSolution(self, arc):
        endAngle = arc.start + arc.length
        endAngleVec = calcs.unitVectorOfAngle(endAngle, arc.rotDirection)
        arcEndPoint = arc.center + arc.radius * endAngleVec
        
        solution = calcs.hitTargetAtSpeed(arcEndPoint, arc.speed, self.getPosition(arc.arcTime()), self.velocity)
        if solution is None:
            raise NoSolutionException
        angle = arc.angleOfVelocity(solution.velocity)
        return angle, solution

