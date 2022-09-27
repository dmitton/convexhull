import math

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()

        # sorted list of points based on x value -- time complexity O(nlogn)
        sorted_points = sorted(points, key=lambda QPointF: QPointF.x())

        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        finalHull = self.solveConvexHull(sorted_points)
        polygon = self.drawPoints(finalHull)
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    def solveConvexHull(self, points):
        if len(points) == 1:
            head = Node(points[0])
            hull = Hull()
            hull.leftMost = head
            hull.rightMost = head
            return hull

        leftHull = self.solveConvexHull(points[:len(points) // 2])
        rightHull = self.solveConvexHull(points[len(points) // 2:])

        # find upper tangent
        upperTangent = self.findUpperTangent(leftHull, rightHull)

        # find lower tangent
        lowerTangent = self.findLowerTangent(leftHull, rightHull)

        # merge the upper and lower
        finalHull = self.combine(upperTangent, lowerTangent, leftHull, rightHull)
        return finalHull

    def findUpperTangent(self, leftHull, rightHull):
        # the node of the right most point on the left hull
        left_Node = leftHull.rightMost
        # the node of the left most point on the right hull
        right_Node = rightHull.leftMost
        # the point of the rightmost point of the left hull
        rightPoint = leftHull.rightMost.point
        # the point of the leftmost point of the right hull
        leftPoint = rightHull.leftMost.point
        # the slope of the two initial points
        temp = self.getSlope(leftPoint, rightPoint)
        done = 0

        while done == 0:
            isUpperTangent = False
            done = 1
            while not isUpperTangent:
                # set the node to the counter clockwise node
                left_Node = left_Node.counter_node
                # set the point to the counter clockwise point
                counter_point = left_Node.counter_node.point
                # calculate the new slope that is between the new point and the leftmost point of the right hull
                new_slope = self.getSlope(leftPoint, counter_point)
                # if the new slope is less than the previous one continue
                if new_slope < temp:
                    # set temp to the new slope
                    temp = new_slope
                    # change the point to the counter clockwise point of the left hull
                    rightPoint = counter_point
                    done = 0
                else:
                    # if it is greater than the previous slope set the left node to the clockwise node
                    isUpperTangent = True
                    left_Node = left_Node.clockwise_node
            isUpperTangent = False
            while not isUpperTangent:
                # set the right node to the clockwise node of the right hull
                right_Node = right_Node.clockwise_node
                # set the point to the clockwise point of the right hull
                clockwise_point = right_Node.clockwise_node.point
                # calculate the slope of the two points
                new_slope = self.getSlope(clockwise_point, rightPoint)
                # if the new slope is greater than the old slope
                if new_slope > temp:
                    # set temp to the new slope
                    temp = new_slope
                    # set the left point of the right hull to the clockwise point
                    leftPoint = clockwise_point
                    done = 0
                else:
                    # if it is greater than the previous slope set the right node to the counter clockwise node
                    isUpperTangent = True
                    right_Node = right_Node.counter_node
        # create a list that will hold the two nodes that make up the tangent
        # append the left node of the upper tangent first
        # append the right node of the upper tangent next
        upperTangentList = [left_Node, right_Node]
        return upperTangentList

    def findLowerTangent(self, leftHull, rightHull):
        # the node of the right most point on the left hull
        left_Node = leftHull.rightMost
        # the node of the left most point on the right hull
        right_Node = rightHull.leftMost
        # the point of the rightmost point of the left hull
        rightPoint = leftHull.rightMost.point
        # the point of the leftmost point of the right hull
        leftPoint = rightHull.leftMost.point
        # the slope of the two initial points
        temp = self.getSlope(leftPoint, rightPoint)
        done = 0

        while done == 0:
            isLowerTangent = False
            done = 1
            while not isLowerTangent:
                # set the node to the clockwise node
                left_Node = left_Node.clockwise_node
                # set the point to the clockwise point
                clockwise_point = left_Node.clockwise_node.point
                # calculate the new slope that is between the new point and the leftmost point of the right hull
                new_slope = self.getSlope(leftPoint, clockwise_point)
                # if the new slope is greater than the previous one continue
                if new_slope > temp:
                    # set temp to the new slope
                    temp = new_slope
                    # change the point to the clockwise point of the left hull
                    rightPoint = clockwise_point
                    done = 0
                else:
                    # if it is less than the previous slope set the left node to the counter clockwise node
                    isLowerTangent = True
                    left_Node = left_Node.counter_node
            isLowerTangent = False
            while not isLowerTangent:
                # set the right node to the counter clockwise node of the right hull
                right_Node = right_Node.counter_node
                # set the point to the counter clockwise point of the right hull
                counter_point = right_Node.counter_node.point
                # calculate the slope of the two points
                new_slope = self.getSlope(counter_point, rightPoint)
                # if the new slope is less than the old slope
                if new_slope < temp:
                    # set temp to the new slope
                    temp = new_slope
                    # set the left point of the right hull to the counter clockwise point
                    leftPoint = counter_point
                    done = 0
                else:
                    # if it is greater than the previous slope set the right node to the counter clockwise node
                    isLowerTangent = True
                    right_Node = right_Node.clockwise_node
        # create a list that will hold the two nodes that make up the tangent
        # append the left node of the lower tangent first
        # append the right node of the lower tangent next
        lowerTangentList = [left_Node, right_Node]
        return lowerTangentList

    def getSlope(self, rightPoint, leftPoint):
        slope = (rightPoint.y() - leftPoint.y()) / (rightPoint.x() - leftPoint.x())
        return slope

    def combine(self, upperTangent, lowerTangent, leftHull, rightHull):
        upperLeft = upperTangent[0]
        upperRight = upperTangent[1]

        upperLeft.clockwise_node = upperRight
        upperRight.counter_node = upperLeft

        lowerLeft = lowerTangent[0]
        lowerRight = lowerTangent[1]

        lowerLeft.counter_node = lowerRight
        lowerRight.clockwise_node = lowerLeft

        finalHull = Hull()
        finalHull.leftMost = leftHull.leftMost
        finalHull.rightMost = rightHull.rightMost
        return finalHull

    def drawPoints(self, finalHull):
        leftMostPoint = finalHull.leftMost
        temp = leftMostPoint.counter_node
        polygon = [QLineF(leftMostPoint.point, temp.point)]
        while temp.point != leftMostPoint.point:
            polygon.append(QLineF(temp.point, temp.counter_node.point))
            temp = temp.counter_node
        return polygon


class Node:
    def __init__(self, data=QPointF):
        self.point = data
        self.counter_node = self
        self.clockwise_node = self


class Hull:
    def __init__(self):
        leftMost = None
        rightMost = None
