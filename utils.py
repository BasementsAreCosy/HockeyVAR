import re
import math
from PIL import ImageTk, Image


def getVectorAngle(vec1, vec2):  # Used for retrieving the angle at which the ball has been deflected per frame
    return math.acos((vec1[0]*vec2[0]+vec1[1]*vec2[1])/(vectorMagnitude(vec1)*vectorMagnitude(vec2)))  # Uses the dot product of 2 vectors to obtain the angle between them

def vectorMagnitude(vec):  # Used in getVectorAngle
    return math.sqrt(vec[0]**2 + vec[1]**2)

def listMean(list):  # Used to get the mean of a set of angles
    return sum(list)/len(list)

def roundToNearest(num, base):  # Used to display the nearest frame to the current time
    return round(num/base)*base

def avgPoint(points):  # Used to draw a line before and after collision
    pointsx = [pos[0] for pos in points]
    pointsy = [pos[1] for pos in points]
    return (round(sum(pointsx)/len(pointsx)), round(sum(pointsy)/len(pointsy)))

def vectorWithinTolerance(target, angle, tolerance):  # Decides whether the ball has had a significant change in direction
    if target+tolerance >= math.pi:
        if 0 <= angle <= target + tolerance - math.pi or target-tolerance <= angle < math.pi:
            return True
        return False
    if target-tolerance < 0:
        if math.pi+(target-tolerance) < angle < math.pi or 0 <= angle <= target+tolerance:
            return True
        return False
    if target-tolerance <= angle <= target+tolerance:
        return True
    return False

def openImage(path):  # Opens an image and converts it to something tkinter can use
    image = Image.open(path)
    image = ImageTk.PhotoImage(image)
    return image

def openImageResize(path, size): # Opens and resizes an image
    image = Image.open(path)
    image.resize(size)
    image = ImageTk.PhotoImage(image)
    return image

def extractFrameNum(e):  # Used for finding the frame number from a path
    return int(re.findall('\d+', e)[-1])  # ex. regular expressions

def getValidRange(p1, p2):  # Used for zooming functionality -> swaps p1 and p2, and xs and ys so p1 s the top left and p2 is the bottom right
    if p2[0] < p1[0]:
        returnedX1 = p2[0]
        returnedX2 = p1[0]
    else:
        returnedX1 = p1[0]
        returnedX2 = p2[0]

    if p2[1] < p1[1]:
        returnedY1 = p2[1]
        returnedY2 = p1[1]
    else:
        returnedY1 = p1[1]
        returnedY2 = p2[1]

    return (returnedX1, returnedY1), (returnedX2, returnedY2)
