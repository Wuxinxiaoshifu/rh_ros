ROS_QUEUE_SIZE = 10

PATHFINDER_NODE_ID = "pathfinder"
PATHFINDER_SERVER_NODE = "action"
PATHFINDER_SERVER = "%s/%s" % (PATHFINDER_NODE_ID, PATHFINDER_SERVER_NODE)
# PATHFINDER_SERVER = "/rh/%s/%s" % (PATHFINDER_NODE_ID, PATHFINDER_SERVER_NODE)

PATHFINDER_INPUT_TOPIC = "%s/input" % PATHFINDER_NODE_ID
PATHFINDER_DEBUG_TOPIC = "%s/debug" % PATHFINDER_NODE_ID

SUBMIT_PROBLEM_SERVICE = "%s/submitProblem" % PATHFINDER_NODE_ID
STEP_PROBLEM_SERVICE = "%s/stepProblem" % PATHFINDER_NODE_ID

