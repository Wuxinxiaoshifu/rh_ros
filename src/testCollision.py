import gui.core
from demos import FindTargetVisualizer, FindTargetProblem
from findPath.obstacleCourse import ObstacleCourse
from geometry.noFlyZone import NoFlyZoneG

noFly1 = NoFlyZoneG([(40, 50), (40, 70), (50, 75), (50, 50)], (3, 0))
noFly2 = NoFlyZoneG([(40, 40), (40, 45), (45, 45), (45, 40)], (-2, 2))

initialFindTargetProblem = FindTargetProblem(ObstacleCourse([noFly1, noFly2], None), (10, 85), 10.0)
window = FindTargetVisualizer(initialFindTargetProblem, 800, 800, 50, 50, 100, 100)

gui.startGUI()
