"""
Utilities for converting ROS messages to/from inputs to the path-finder.
"""
import math
from pathfinding.msg._Arc import Arc
import pathfinding.msg._DynamicNoFlyZone
import pathfinding.msg._NoFlyZone 
import pathfinding.msg._Params
from pathfinding.msg._PathDebug import PathDebug
from pathfinding.msg._PathSegment import PathSegment
import pathfinding.msg._Road
import pathfinding.msg._Scenario
import pathfinding.msg._SolutionWaypoint
import pathfinding.msg._Vehicle

from engine.geometry.pathSegment.arcPathSegment import ArcPathSegment
import engine.interface.dynamicNoFlyZone
from engine.interface.gpsTransform.gpsTransform import GPSTransformer
import engine.interface.noFlyZone
import engine.interface.pathFindParams
import engine.interface.road
import engine.interface.scenario
import engine.interface.solutionWaypoint
import engine.interface.vehicle
import numpy as np


#**********************Msg objects to path finding objects********************
class MessageConverter:

    def __init__(self, gpsRef):
        self._gpsTransformer = GPSTransformer(gpsRef)

    def msgToParams(self, inputParamsMsg):
        return engine.interface.pathFindParams.PathFindParams(float(inputParamsMsg.waypointAcceptanceRadii),
                                  float(inputParamsMsg.nfzBufferSize))
    
    def msgToVehicle(self, msg):
        return engine.interface.vehicle.Vehicle(float(msg.maxSpeed), float(msg.acceleration))
    
    def msgToScenario(self, msg):
        noFlyZones = []
        for noFlyZone in msg.noFlyZones:
            noFlyZones.append(self.msgToNoFlyZone(noFlyZone)) 
        dynamicNoFlyZones = []
        for dNoFlyZone in msg.dynamicNoFlyZones:
            dynamicNoFlyZones.append(self.msgToDynamicNoFlyZone(dNoFlyZone)) 
            
        roads = []
        for road in msg.roads:
            roads.append(self.msgToRoad(road))
        
        return engine.interface.scenario.Scenario(
                        self.msgToPointList(msg.boundaryPoints),
                        noFlyZones,
                        dynamicNoFlyZones,
                        roads,
                        self.msgToPoint(msg.startPoint),
                        self.msgToVector(msg.startVelocity),
                        self.msgToPointList(msg.wayPoints))
    
    def msgToRoad(self, msg):
        return engine.interface.road.Road(self.msgToPoint(msg.startPoint), self.msgToPoint(msg.startPoint), float(msg.width))
    
    def msgToNoFlyZone(self, msg):
        return engine.interface.noFlyZone.NoFlyZone(
            self.msgToPointList(msg.points),
            self.msgToVector(msg.velocity),
            int(msg.ID))

    def msgToDynamicNoFlyZone(self, msg):
        return engine.interface.dynamicNoFlyZone.DynamicNoFlyZone(
            self.msgToPoint(msg.center),
            float(msg.radius),
            self.msgToVector(msg.velocity),
            int(msg.ID))
        
    def msgToPointList(self, msg):
        pointList = []
        for pointMsg in msg:
            pointList.append(self.msgToPoint(pointMsg))
        return pointList
    
    def msgToPathDebug(self, msg):
        pastPathSegments = self.msgToPathSegmentList(msg.pastPathSegments)
        futurePathSegments = self.msgToPathSegmentList(msg.futurePathSegments)
        filteredPathSegments = self.msgToPathSegmentList(msg.filteredPathSegments)
        return (pastPathSegments, futurePathSegments, filteredPathSegments)
    
    def msgToSolutionWaypointList(self, msg):
        solutionWaypoints = []
        for solutionWaypointMsg in msg:
            solutionWaypoints.append(self.msgToSolutionWaypoint(solutionWaypointMsg))
        return solutionWaypoints

    def msgToSolutionWaypoint(self, msg):
        return engine.interface.solutionWaypoint.SolutionWaypoint(self.msgToPoint(msg.position), float(msg.radius))
    
    def msgToPathSegmentList(self, msg):
        pathSegments = []
        for pathSegmentMsg in msg:
            pathSegments.append(self.msgToPathSegment(pathSegmentMsg))
        return pathSegments
    
    def msgToPathSegment(self, msg): 
#         (self, startTime, elapsedTime, lineStartPoint, endPoint, endSpeed, endDirection, arc):
        endVelocity = self.msgToVector(msg.endVelocity)
        endSpeed = np.linalg.norm(endVelocity)
        endUnitVelocity = endVelocity / endSpeed
        return ArcPathSegment(float(msg.startTime),
                                     float(msg.elapsedTime),
                                     self.msgToPoint(msg.lineStartPoint),
                                     self.msgToPoint(msg.endPoint),
                                     endSpeed,
                                     endUnitVelocity,
                                     self.msgToArc(msg.arc))
                
    def msgToArc(self, msg):
        if msg.length < 0.0:
            rotDirection = 1.0
            length = -math.radians(float(msg.length))
        else:
            rotDirection = -1.0
            length = math.radians(float(msg.length))
            
        start = self._gpsTransformer.gpsAngleToLocal(float(msg.start), rotDirection)

        return engine.geometry.arc.Arc(rotDirection,
                                      float(msg.radius),
                                      self.msgToPoint(msg.center),
                                      start,
                                      length)
    
    #**********************Path finding objects to msg objects********************
    def paramsToMsg(self, inputParams):
        msg = pathfinding.msg._Params.Params()
        msg.waypointAcceptanceRadii = inputParams.waypointAcceptanceRadii
        msg.nfzBufferSize = inputParams.nfzBufferSize
        return msg
    
    def vehicleToMsg(self, vehicle):
        msg = pathfinding.msg._Vehicle.Vehicle()
        msg.maxSpeed = vehicle.maxSpeed
        msg.acceleration = vehicle.acceleration
        return msg
    
    def scenarioToMsg(self, scenario):
        msg = pathfinding.msg._Scenario.Scenario()
        msg.boundaryPoints = self.pointListToMsg(scenario.boundaryPoints)
        msg.noFlyZones = []
        msg.dynamicNoFlyZones = []
        
        for noFlyZone in scenario.noFlyZones:
            msg.noFlyZones.append(self.nfzToMsg(noFlyZone))
        for dNoFlyZone in scenario.dynamicNoFlyZones:
            msg.dynamicNoFlyZones.append(self.dnfzToMsg(dNoFlyZone))
            
        for road in scenario.roads:
            msg.roads.append(self.roadToMsg(road))
        msg.startPoint = self.pointToMsg(scenario.startPoint)
        msg.startVelocity = self.vectorToMsg(scenario.startVelocity)
        msg.wayPoints = self.pointListToMsg(scenario.wayPoints)
        return msg
    
    def roadToMsg(self, road):
        msg = pathfinding.msg._Road.Road()
        msg.startPoint = self.pointToMsg(road.startPoint)
        msg.endPoint = self.pointToMsg(road.endPoint)
        msg.width = road.width
        return msg
        
    def nfzToMsg(self, noFlyZone):
        msg = pathfinding.msg._NoFlyZone.NoFlyZone()
        msg.points = self.pointListToMsg(noFlyZone.points)
        msg.velocity = self.vectorToMsg(noFlyZone.velocity)
        msg.ID = noFlyZone.ID
        return msg
    
    def dnfzToMsg(self, dNoFlyZone):
        msg = pathfinding.msg._DynamicNoFlyZone.DynamicNoFlyZone()
        msg.center = self.pointToMsg(dNoFlyZone.center)
        msg.radius = dNoFlyZone.radius
        msg.velocity = self.vectorToMsg(dNoFlyZone.velocity)
        msg.ID = dNoFlyZone.ID
        return msg
        
    def pointListToMsg(self, points):
        msg = []
        for point in points:
            msg.append(self.pointToMsg(point))
        return msg
    
    def pathDebugToMsg(self, pastPathSegments, futurePathSegments, filteredPathSegments):
        msg = PathDebug()
        msg.pastPathSegments = self.pathSegmentListToMsg(pastPathSegments)
        msg.futurePathSegments = self.pathSegmentListToMsg(futurePathSegments)
        msg.filteredPathSegments = self.pathSegmentListToMsg(filteredPathSegments)
        return msg
    
    def solutionWaypointListToMsg(self, solutionWaypoints):
        msg = []
        for solutionWaypoint in solutionWaypoints:
            msg.append(self.solutionWaypointToMsg(solutionWaypoint))
        return msg

    def solutionWaypointToMsg(self, solutionWaypoint):
        msg = pathfinding.msg._SolutionWaypoint.SolutionWaypoint() 
        msg.position = self.pointToMsg(solutionWaypoint.position)
        msg.radius = solutionWaypoint.radius
        return msg
        
    def pathSegmentListToMsg(self, pathSegments):
        msg = []
        for pathSegment in pathSegments:
            msg.append(self.pathSegmentToMsg(pathSegment))
        return msg
    
    def pathSegmentToMsg(self, pathSegment):
        if isinstance(pathSegment, ArcPathSegment):
            msg = PathSegment()
            msg.startTime = pathSegment.startTime
            msg.elapsedTime = pathSegment.elapsedTime
            msg.speed = pathSegment.speed
            msg.arc = self.arcToMsg(pathSegment.arc)
            msg.lineStartPoint = self.pointToMsg(pathSegment.lineStartPoint)
            msg.endPoint = self.pointToMsg(pathSegment.endPoint)
            msg.endVelocity = self.vectorToMsg(pathSegment.endUnitVelocity * pathSegment.endSpeed)
            return msg
        else:
            raise "Path segment type not suppored by messages"
                
    def arcToMsg(self, arc):
        msg = Arc()
        msg.radius = arc.radius
        msg.center = self.pointToMsg(arc.center)
        msg.start = self._gpsTransformer.localAngleToGPS(arc.start, arc.rotDirection)
        msg.length = math.degrees(arc.length) * -arc.rotDirection
        return msg

#***************************Point/vector Conversions*****************************

    def msgToPoint(self, msg):
        return self._gpsTransformer.gpsToLocal(msg)
         
    def pointToMsg(self, point):
        return self._gpsTransformer.localToGPS(point)
 
    def msgToVector(self, msg):
        return self._gpsTransformer.gpsVelocityToLocal(msg)
         
    def vectorToMsg(self, vec):
        return self._gpsTransformer.localToGPSVelocity(vec)
