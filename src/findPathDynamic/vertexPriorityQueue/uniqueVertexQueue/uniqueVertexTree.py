import numpy as np
from typing import Union

_subIndexMultipliers = np.array([1, 2, 4, 8], np.int32)


def _calcIndex(subIndices):
    return int(np.dot(subIndices, _subIndexMultipliers))


def checkCoincident(p1, p2):
    # type: (np.ndarray,np.ndarray)->bool
    """
    Determines if each component of p1 is the same as p2.
    :param p1:
    :param p2:
    :return:
    """
    return (p1 == p2).sum() == 4


# Not clear what the best data structure is for this. Numpy supports kd-trees and Voronoi diagrams, but:
# kd-trees are not considered good in dynamic situations.
# Voronoi uses n^2 space, not clear if this is good for dynamic situations.
# R-trees are supposed to be good for dynamics, but they don't appear to be supported out of the box (there is some GIS version on the web).
# In a recent test, insertion into this tree accounted for ~1.2% of the computation time, so this is NOT the place to optimize.

class UniqueTree:
    """
    A 4-d quadtree-ish data structure used to determine uniqueness value.  Every node in the tree has a uniqueness
    value proportional to the size of its edge.  The root has a uniqueness of 1.0 and each level down the
    tree has 1/2 the uniqueness of the previous level.

    For efficiency this does not check for illegal values outside the range of the cell.  DON'T INSERT THESE VALUES!
    """

    def __init__(self, x, y, width, height, maximumSpeed):
        minPosition = np.array([x, y, -maximumSpeed, -maximumSpeed], np.double)
        dims = np.array([width, height, 2.0 * maximumSpeed, 2.0 * maximumSpeed], np.double)

        self._root = UniqueNode(minPosition, dims, uniqueness=0.5)
        self._empty = True

    def insert(self, vertex):
        """
        Insert the vertex and return a uniqueness score.
        :param vertex:
        :return:
        """
        position = np.array([vertex.position[0], vertex.position[1], vertex.velocity[0], vertex.velocity[1]])

        # TODO: OK I lied.  For now we do check this.  However, we'll remove this check once the geo-fence is in place.
        if (position < self._root._minPosition).sum() + (
                position >= (self._root._minPosition + self._root._dims)).sum() > 0:
            return 0.0

        if self._empty:
            self._empty = False
            self._root.insert(position)
            return 1.0

        return self._root.insert(position)


class UniqueNode:
    """
    Handles the work of actually inserting positions into sub-trees.
    """

    def __init__(self, minPosition, dims, uniqueness):
        """
        :param minPosition: The "upper-left" corner of the 4-d cell.
        :param dims: The dimensions of the 4-d cell
        :param uniqueness: The uniqueness value of this node.  Anything point directly inserted into the child array has this uniqueness value.
        """
        self._minPosition = np.array(minPosition, np.double)  # type: np.ndarray
        self._dims = np.array(dims, np.double)  # type: np.ndarray
        self._halfDims = self._dims / 2.0  # type: np.ndarray

        # Each slot contains a position OR an entire sub-tree
        self._children = [None] * 16  # type: Union[np.ndarray, UniqueNode]
        self._uniqueness = uniqueness  # type: float

    def insert(self, position):
        """
        Inserts the position into one of the 16 available children of node.
        This will recurse if the child is not empty.
        :param position:
        :return:
        """
        subIndices = self._calcSubIndices(position)
        index = _calcIndex(subIndices)

        # If the slot is empty just insert the position there
        if self._children[index] is None:
            self._children[index] = position
            return self._uniqueness

        # If there is not a sub-tree at the index we want to insert at then we need to create one
        elif not isinstance(self._children[index], UniqueNode):
            existingPosition = self._children[index]

            # This point already exists.  Don't insert it and return a uniqueness of 0.0!
            if checkCoincident(position, existingPosition):
                return 0.0
            subTree = self._createSubTree(subIndices)
            self._children[index] = subTree

            # Insert the existing position into the subtree 1st
            subTree.insert(existingPosition)

        return self._children[index].insert(position)

    def _createSubTree(self, subIndices):
        """
        Create a new sub-tree root based on this cell and the given sub-indices.
        :param subIndices:
        :return:
        """
        subCellPosition = self._minPosition + subIndices * self._halfDims
        return UniqueNode(subCellPosition, self._halfDims, self._calcSubUniqueness())

    def _calcSubIndices(self, position):
        """
        Given a position, determine its "sub-indices".  This is a 4-element array of 0|1 determining if this goes
        "left" or "right" for each dimension.

        :param position:
        :return:
        """
        ratios = (position - self._minPosition)
        ratios /= self._halfDims
        subIndices = ratios.astype(np.int32)
        return subIndices

    def _calcSubUniqueness(self):
        """
        Determines a sub-tree's uniqueness based on this tree's uniqueness.
        :return:
        """
        return self._uniqueness / 2.0
