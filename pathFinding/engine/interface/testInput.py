import numpy as np
class TestInput():
    """
    Input used in testing.  Defines the problem of finding a PathSegment from 
    a starting point with an initial velocity to a moving target.
    """
    def __init__(self, startPoint, startVelocity, targetPoint, velocityOfTarget):
        self.startPoint = np.array(startPoint, np.double)
        self.startVelocity = np.array(startVelocity, np.double)
        self.targetPoint = np.array(targetPoint, np.double)
        self.velocityOfTarget = np.array(velocityOfTarget, np.double)