import math

from engine.interface.solutionWaypoint import SolutionWaypoint

MAX_WAYPOINT_ARC_LENGTH = math.pi - 0.01


class OutputPath:
    """
    Represents a path generated by the path finder.  The path may or may not be complete.
    """

    def __init__(self, pathWaypoints, pathSegments, quality, numWayPointsCompleted, estimatedTime):
        self.pathWaypoints = pathWaypoints
        self.pathSegments = pathSegments
        self.numWayPointsCompleted = numWayPointsCompleted
        self.quality = quality
        self.estimatedTime = estimatedTime


def generatePath(endVertex, waypointAcceptanceRadii, quality, numWayPointsCompleted):
    pathSegments = endVertex.generatePathSegments()
    pathWaypoints = _calcSolutionWaypoints(pathSegments, waypointAcceptanceRadii)
    return OutputPath(pathWaypoints, pathSegments, quality, numWayPointsCompleted, endVertex.getTimeThroughHeuristic())


def _calcSolutionWaypoints(pathSegments, waypointAcceptanceRadii):
    solutionWaypoints = []
    for pathSegment in pathSegments:
        
        # We are arcing close to 180 degrees.  To force flight controller to loop in this direction, add waypoint
        arc = pathSegment.arc 
        if pathSegment.arc.length > MAX_WAYPOINT_ARC_LENGTH:
            estimatedTime = pathSegment.startTime + arc.arcTime(MAX_WAYPOINT_ARC_LENGTH)
            (position, direction) = arc.endInfoLength(MAX_WAYPOINT_ARC_LENGTH)
            solutionWaypoints.append(SolutionWaypoint(position, waypointAcceptanceRadii, estimatedTime, direction))
        
        position = pathSegment.endPoint + pathSegment.endUnitVelocity * waypointAcceptanceRadii
        solutionWaypoints.append(SolutionWaypoint(position, waypointAcceptanceRadii, pathSegment.startTime + pathSegment.elapsedTime, pathSegment.endUnitVelocity))
        
    return solutionWaypoints
