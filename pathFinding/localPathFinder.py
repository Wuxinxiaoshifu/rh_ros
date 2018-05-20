"""
Runs a local path finder instance (no ROS).  This is convenient for debugging.
"""
from gui.pathFinder.guiPathFinderInterface import LocalPathFinderInterface
import gui
from gui.pathFinder.pathFindViewer import PathFindViewer

PathFindViewer(LocalPathFinderInterface(), 800, 800)

gui.startGUI()
