cmake_minimum_required(VERSION 2.8.3)
project(rh_msgs)

find_package(catkin REQUIRED COMPONENTS 
    geometry_msgs sensor_msgs geographic_msgs message_generation std_msgs mavros_msgs)

add_message_files(
  DIRECTORY msg
  FILES
  Point2D.msg
  PointList.msg
  GPSCoord.msg
  GPSCoordList.msg
  Mission.msg
  State.msg
  VehicleState.msg
  CameraMetadata.msg
)

add_service_files(
  DIRECTORY srv
  FILES
  Land.srv
  TakeOff.srv
  FlyTo.srv
  SetMission.srv
  SetNoFlyZones.srv
  GetState.srv
  StartMission.srv
  AbortMission.srv
  FlyWaypoints.srv
  GenerateSearchPattern.srv
  GetCameraMetadata.srv
)

generate_messages(DEPENDENCIES geometry_msgs sensor_msgs geographic_msgs std_msgs mavros_msgs)

catkin_package(
  CATKIN_DEPENDS geometry_msgs sensor_msgs geographic_msgs message_runtime std_msgs mavros_msgs)

