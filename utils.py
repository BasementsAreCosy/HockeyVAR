import re
import math
from PIL import ImageTk, Image

def getVectorAngle(vec1, vec2):
    return math.acos((vec1[0]*vec2[0]+vec1[1]*vec2[1])/(vectorMagnitude(vec1)*vectorMagnitude(vec2)))

def vectorMagnitude(vec):
    return math.sqrt(vec[0]**2 + vec[1]**2)

def listMean(list):
    return sum(list)/len(list)

def roundToNearest(num, base):
    return round(num/base)*base

def avgPoint(points):
    pointsx = [pos[0] for pos in points]
    pointsy = [pos[1] for pos in points]
    return (round(sum(pointsx)/len(pointsx)), round(sum(pointsy)/len(pointsy)))

def vectorWithinTolerance(target, angle, tolerance):
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

def openImage(path):
    image = Image.open(path)
    image = ImageTk.PhotoImage(image)
    return image

def openImageResize(path, size):
    image = Image.open(path)
    image.resize(size)
    image = ImageTk.PhotoImage(image)
    return image

def extractFrameNum(e):
    return int(re.findall('\d+', e)[0])  # Used for finding the frame number from a path

def getValidRange(p1, p2):
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
