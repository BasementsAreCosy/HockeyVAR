import cv2
import os
import glob
import time
import utils
import tkinter as tk
from PIL import ImageTk, Image
import math
import numpy as np

class HockeyVideo:
    def __init__(self, root, path, frameJump=1, debug=False):

        # CONSTANTS - Python doesn't support this natively
        self.root = root  # Tkinter window
        self.root.bind('<Escape>', self.endManualVAR)
        self.path = path  # Video path
        self.frame = tk.Frame(self.root, bg='green')  # Initialise the tkinter frame which holds the video
        self.footIdentified = False
        self.lastImage = None
        self.currentImage = None
        self.mouseX = None
        self.mouseY = None
        self.previewX = None
        self.previewY = None
        self.boundingBox = {'topLeft': None, 'width': None, 'height': None}
        self.scale = 1
        self.frameJump = frameJump  # How many frames are displayed e.g: frameJump = 2, only frame 0, 2, 4, 6 will play
        self.fps = 30  # Video FPS, redefined when a video is submitted. 30 is standard?
        self.size = (750, 500)
        if not debug:
            self.separateFrames()  # Turns the video into a sequence of frames
        self.frames = glob.glob('footage/*')  # Creates a list of frame paths
        self.frames.sort(key=utils.extractFrameNum)  # Sorts into order
        self.lastFrame = utils.extractFrameNum(self.frames[-1])  # path of the last frame
        self.frameNum = 0  # Current frame being displayed
        self.nextFrameDisplayTime = time.time()  # Time when the next frame should display
        self.speed = 1  # Playback speed
        self.isPaused = False
        self.videoEnded = False  # Ends video threading when True
        self.manualVARMode = False
        self.VARStage = [0, 'left']
        self.endStage = 5
        self.ballHistory = []
        self.ballCollisionIndex = None

    def separateFrames(self):
        files = glob.glob('footage/*')
        for f in files:
            os.remove(f)  # Clears frame directory

        vidObj = cv2.VideoCapture(self.path)
        self.fps = vidObj.get(cv2.CAP_PROP_FPS)

        count = 0
        success = 1
        while success:
            try:
                success, image = vidObj.read()
                if count % self.frameJump == 0:
                    image = cv2.resize(image, self.size, interpolation=cv2.INTER_CUBIC)
                    cv2.imwrite(f'footage/{count}.jpg', image)  # Creates frame file, form orderSequence-modelConfidence
                count += 1
            except:
                print('End of video?')

    def displayFrames(self): # ONLY INVOKE AS THREAD
        comparisonFrameDifference = 10
        self.nextFrameDisplayTime = time.time()
        while True: # Thread: so while video exists, this always runs
            if self.videoEnded:
                return  # When returned, the thread ends
            if not self.manualVARMode:
                frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                self.displayImageInFrame(1, 0, frameName=frameName)
                while self.speed == 0 or self.isPaused:
                    if self.videoEnded:
                        return  # When returned, the thread ends
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.displayImageInFrame(1, 0, frameName=frameName)

                self.nextFrameDisplayTime += (self.frameJump/self.fps)/self.speed
                if self.nextFrameDisplayTime - time.time() >= 0:  # Wait until time to show next frame
                    time.sleep(self.nextFrameDisplayTime - time.time())
                if self.footIdentified:  # Stutter frame when foot identified
                    self.footIdentified = False
                    time.sleep(1)
                    self.VARStage[1] = 'left'
                    self.manualVARMode = True
                    self.mouseX = None
                    self.mouseY = None
                    self.frameNum -= comparisonFrameDifference/2
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.VARInstructionLabel = tk.Label(self.root, text=f'Please select the {self.VARStage[1]}-most point of the ball.')
                    self.VARInstructionLabel.grid(row=0, column=2)
                    self.displayImageInFrame(1, 0, frameName=frameName)
                elif utils.roundToNearest(self.frameNum + self.frameJump, self.frameJump) <= self.lastFrame:
                    self.frameNum += self.frameJump
                else:  # End of video
                    self.displayImageInFrame(1, 0, frameName=frameName)
                    self.isPaused = True
            if self.manualVARMode:
                if self.VARStage[0] < self.endStage:
                    self.displayVARImage(frameName)
                    if self.mouseX != None and self.mouseY != None:
                        if self.VARStage[1] == 'left':
                            clickLocation = (self.mouseX, self.mouseY)
                            self.mouseX = None
                            self.mouseY = None
                            self.VARStage[1] = 'right'
                        elif self.VARStage[1] == 'right':
                            self.ballHistory.append((self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump], ((clickLocation[0]+self.mouseX)//2, self.mouseY), abs(self.mouseX-clickLocation[0])//2))
                            frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                            self.mouseX = None
                            self.mouseY = None
                            self.VARStage[0] += 1
                            self.VARStage[1] = 'left'
                            while frameName == self.ballHistory[-1][0] or frameName == None:
                                if utils.roundToNearest(self.frameNum + comparisonFrameDifference/self.endStage, self.frameJump) <= self.lastFrame:
                                    self.frameNum += comparisonFrameDifference/self.endStage
                                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                        self.VARInstructionLabel = tk.Label(self.root,
                                                            text=f'Please select the {self.VARStage[1]}-most point of the ball.')
                        self.VARInstructionLabel.grid(row=0, column=2)
                else:
                    self.displayVARResult()
                    while self.manualVARMode:
                        pass
                    self.ballHistory = []
                    self.ballCollisionIndex = None
                    self.VARStage[0] = 0
                    self.endVARButton = tk.Button(self.root, text='Continue', command=self.endVAR)
                    self.endVARButton.grid(row=0, column=1)
                    self.endVARButton.destroy()
                    self.VARInstructionLabel.destroy()
                    if self.frameNum + self.frameJump <= self.lastFrame:
                        self.frameNum += comparisonFrameDifference
                    self.nextFrameDisplayTime = time.time()
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.displayImageInFrame(1, 0, frameName=frameName)

    def endVAR(self):
        self.manualVARMode = False

    def displayVARResult(self):
        self.boundingBox = {'topLeft': None, 'width': None, 'height': None}
        pointsBeforeCollision = []
        pointsAfterCollision = []
        vectors = []
        angles = []
        averageAngle = 0
        postCollisionIndexes = []
        for i in range(len(self.ballHistory) - 1):
            vectors.append((self.ballHistory[i + 1][1][0] - self.ballHistory[i][1][0], self.ballHistory[i + 1][1][1] - self.ballHistory[i][1][1]))
        for i in range(len(vectors)-1):
            angles.append(utils.getVectorAngle(vectors[i], vectors[i+1]))
            if utils.vectorWithinTolerance(averageAngle, angles[-1], math.pi / 8):
                averageAngle = utils.listMean(angles)
            else:
                angles.pop(-1)
                postCollisionIndexes.append(i)
        if postCollisionIndexes != []:
            collisionIndex = min(postCollisionIndexes) + 1
        else:
            collisionIndex = self.endStage - 1
        image = cv2.imread(self.ballHistory[collisionIndex][0])
        for i in range(len(self.ballHistory)):
            if i < collisionIndex:
                pointsBeforeCollision.append(self.ballHistory[i][1])
                colour = (0, 255, 0)
            elif i == collisionIndex:
                colour = (0, 127, 255)
            else:
                pointsAfterCollision.append(self.ballHistory[i][1])
                colour = (0, 0, 255)
            cv2.circle(img=image, center=self.ballHistory[i][1], radius=self.ballHistory[i][2], color=colour, thickness=1)
        cv2.line(img=image, pt1=self.ballHistory[collisionIndex][1],
                 pt2=utils.avgPoint(pointsBeforeCollision),
                 color=(0, 255, 0), thickness=2)
        if postCollisionIndexes != []:
            cv2.line(img=image, pt1=self.ballHistory[collisionIndex][1],
                     pt2=utils.avgPoint(pointsAfterCollision),
                     color=(0, 0, 255), thickness=2)
        self.displayImageInFrame(1, 0, image=image)

    def displayVARImage(self, frameName):
        image = cv2.imread(frameName)
        for pos in self.ballHistory:
            cv2.circle(img=image, center=pos[1], radius=pos[2], color=(0, 255, 0), thickness=2)
        self.displayImageInFrame(1, 0, image=image)

    def displayImageInFrame(self, row, column, frameName=None, image=None):
        if frameName != None:
            image = cv2.imread(frameName)
            self.frame.configure(bg='green' if not self.footIdentified else 'red')
        else:
            self.frame.configure(bg='red')
        if self.boundingBox['topLeft'] != None and self.boundingBox['width'] != None and self.boundingBox['height'] != None:
            image = image[self.boundingBox['topLeft'][1]:self.boundingBox['topLeft'][1]+self.boundingBox['height'], self.boundingBox['topLeft'][0]:self.boundingBox['topLeft'][0]+self.boundingBox['width']]
            image = self.zoomOnBoundingBox(image)
        elif self.boundingBox['topLeft'] != None:
            topLeft, bottomRight = utils.getValidRange(self.boundingBox['topLeft'], (self.previewX, self.previewY))
            previewBox = image[topLeft[1]:bottomRight[1], topLeft[0]:bottomRight[0]]
            previewBox = np.clip(previewBox + 50, 0, 255)
            image[topLeft[1]:bottomRight[1], topLeft[0]:bottomRight[0]] = previewBox
        frameImg = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
        if self.lastImage != None:
            self.lastImage.destroy()
        if self.currentImage != None:
            self.lastImage = self.currentImage
        self.currentImage = tk.Label(self.frame, image=frameImg)
        self.currentImage.image = frameImg
        self.currentImage.grid(row=0, column=0, padx=5, pady=5)
        self.currentImage.bind('<Button-1>', self.getMouseBallPos)
        self.currentImage.bind('<Button-3>', self.createBoundingBox)
        self.currentImage.bind('<Motion>', self.getMousePreviewBox)
        self.frame.grid(row=row, column=column, columnspan=6)

    def getMouseBallPos(self, event):
        if self.manualVARMode:
            self.mouseX = event.x
            self.mouseY = event.y
            if self.boundingBox['topLeft'] != None and self.boundingBox['width'] != None and self.boundingBox['height'] != None:
                self.mouseX = round((self.mouseX/self.scale) + self.boundingBox['topLeft'][0])
                self.mouseY = round((self.mouseY/self.scale) + self.boundingBox['topLeft'][1])

    def createBoundingBox(self, event):
        if self.boundingBox['topLeft'] == None:
            self.boundingBox['topLeft'] = [event.x, event.y]
        elif self.boundingBox['width'] == None or self.boundingBox['height'] == None:
            self.boundingBox['width'] = abs(event.x-self.boundingBox['topLeft'][0])
            self.boundingBox['height'] = abs(event.y-self.boundingBox['topLeft'][1])
            if event.x < self.boundingBox['topLeft'][0]:
                self.boundingBox['topLeft'][0] = event.x
            if event.y < self.boundingBox['topLeft'][1]:
                self.boundingBox['topLeft'][1] = event.y
        else:
            self.boundingBox = {'topLeft': None, 'width': None, 'height': None}

    def getMousePreviewBox(self, event):
        self.previewX = event.x
        self.previewY = event.y

    def zoomOnBoundingBox(self, image):
        height, width = image.shape[:2]
        self.scale = min(self.size[0] / width, self.size[1] / height)
        image = cv2.resize(image, (0, 0), fx=self.scale, fy=self.scale)
        return image

    def endManualVAR(self, event):
        self.manualVARMode = False