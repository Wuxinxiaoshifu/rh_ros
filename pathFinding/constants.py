# TODO: Tune values
# When computing _straightPaths to vertices of no-fly-zones, choosing the exact vertex may register as a collision due to
# round-off error.  This small delta offset, outward along the vertices's normal prevents this.
import math

DEFAULT_MAX_VEHICLE_SPEED = 60.0
DEFAULT_TURN_ACCELERATION = 9.8
DEFAULT_WAYPOINT_ACCEPTANCE_RADII = 50.0
DEFAULT_NFZ_BUFFER_SIZE = 10.0

IDENTICAL_POINT_TOLERANCE = 0.1

# This is used to determine if 2 points are identical (is the distance squared between them less than this)
DISTANCE_TOLERANCE_SQUARED = IDENTICAL_POINT_TOLERANCE * IDENTICAL_POINT_TOLERANCE

CANBERRA_GPS = (-35.2809, 149.1300)

# A good worst case would be if start an end were at diagonals of a square 
# and the path were a completely straight line.  If the boundaries were just barely surrounding
# this square, then the diagonal would be ~11km (6 nautical miles).  The edges of the square would be 11km/sqrt(2)
COURSE_DIM = 11000.0 / math.sqrt(2.0)
