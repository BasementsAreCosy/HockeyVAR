import copy
import cv2
import os
import glob
import time
import utils
import tkinter as tk
from PIL import ImageTk, Image

class HockeyVideo:
    def __init__(self, root, path, frameJump=1, debug=False):
        self.root = root  # Tkinter window
        self.root.bind('<Escape>', self.endManualVAR)
        self.path = path  # Video path
        self.frame = tk.Frame(self.root, bg='green')  # Initialise the tkinter frame which holds the video
        self.lastImage = None
        self.currentImage = None
        self.mouseX = None
        self.mouseY = None
        self.frameJump = frameJump  # How many frames are displayed e.g: frameJump = 2, only frame 0, 2, 4, 6 will play
        self.fps = 30  # Video FPS, redefined when a video is submitted. 30 is standard?
        if not debug:
            self.separateFrames()  # Turns the video into a sequence of frames
        utils.tempClassifyFramesRand()  # Randomly assigns values to the frames (no model working yet)
        self.frames = glob.glob('footage/*')  # Creates a list of frame paths
        self.frames.sort(key=utils.extractFrameNum)  # Sorts into order
        self.lastFrame = utils.extractFrameNum(self.frames[-1])  # path of the last frame
        self.frameNum = 0  # Current frame being displayed
        self.nextFrameDisplayTime = time.time()  # Time when the next frame should display
        self.speed = 1  # Playback speed
        self.isPaused = False
        self.videoEnded = False  # Ends video threading when True
        self.manualVARMode = False
        self.VARStage = 0
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
                    image = cv2.resize(image, (750, 500), interpolation=cv2.INTER_CUBIC)
                    cv2.imwrite(f'footage/{count}-predval.jpg', image)  # Creates frame file, form orderSequence-modelConfidence
                count += 1
            except:
                print('End of video?')

    def displayFrames(self): # ONLY INVOKE AS THREAD
        comparisonFrameDifference = 12
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
                if utils.extractConfidenceVal(frameName) == 1:  # Stutter frame when foot identified
                    time.sleep(1)
                    self.isPaused = True
                    self.VARStage = 0
                    self.manualVARMode = True
                    self.frameNum -= comparisonFrameDifference/2
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.VARInstructionLabel = tk.Label(self.root, text=f'Please select the centre of the ball.')
                    self.VARInstructionLabel.grid(row=0, column=1)
                    self.displayImageInFrame(1, 0, frameName=frameName)
                elif utils.roundToNearest(self.frameNum + self.frameJump, self.frameJump) <= self.lastFrame:
                    self.frameNum += self.frameJump
                else:  # End of video
                    self.displayImageInFrame(1, 0, frameName=frameName)
                    self.isPaused = True
            if self.manualVARMode:
                if self.VARStage < self.endStage:
                    if self.mouseX != None and self.mouseY != None:
                        self.ballHistory.append((self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump], (self.mouseX, self.mouseY), 5))
                        frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                        if utils.extractConfidenceVal(frameName) != 0:
                            self.ballCollisionIndex = len(self.ballHistory) - 1
                        self.mouseX = None
                        self.mouseY = None
                        self.VARStage += 1
                        while frameName == self.ballHistory[-1][0] or frameName == None:
                            if utils.roundToNearest(self.frameNum + comparisonFrameDifference/self.endStage, self.frameJump) <= self.lastFrame:
                                self.frameNum += comparisonFrameDifference/self.endStage
                                frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                        self.displayVARImage(frameName)
                else:
                    self.displayVARResult()
                    self.ballHistory = []
                    self.ballCollisionIndex = None
                    time.sleep(3)
                    self.VARInstructionLabel.destroy()
                    self.manualVARMode = False
                    if self.frameNum + self.frameJump <= self.lastFrame:
                        self.frameNum += comparisonFrameDifference
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.displayImageInFrame(1, 0, frameName=frameName)

    def displayVARResult(self):
        pointsBeforeCollision = []
        pointsAfterCollision = []
        image = cv2.imread(self.ballHistory[self.ballCollisionIndex][0])
        for i in range(len(self.ballHistory)):
            if i < self.ballCollisionIndex:
                pointsBeforeCollision.append(self.ballHistory[i][1])
                colour = (0, 255, 0)
            elif i == self.ballCollisionIndex:
                colour = (0, 127, 255)
            else:
                pointsAfterCollision.append(self.ballHistory[i][1])
                colour = (0, 0, 255)
            cv2.circle(img=image, center=self.ballHistory[i][1], radius=self.ballHistory[i][2], color=colour, thickness=1)
        cv2.line(img=image, pt1=self.ballHistory[self.ballCollisionIndex][1],
                 pt2=utils.avgPoint(pointsBeforeCollision),
                 color=(0, 255, 0), thickness=2)
        cv2.line(img=image, pt1=self.ballHistory[self.ballCollisionIndex][1],
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
            frameImg = utils.openImage(frameName)
            self.frame.configure(bg='green' if utils.extractConfidenceVal(frameName) == 0 else 'red')
        else:
            frameImg = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
            self.frame.configure(bg='red')
        if self.lastImage != None:
            self.lastImage.destroy()
        if self.currentImage != None:
            self.lastImage = self.currentImage
        self.currentImage = tk.Label(self.frame, image=frameImg)
        self.currentImage.image = frameImg
        self.currentImage.grid(row=0, column=0, padx=5, pady=5)
        self.currentImage.bind('<Button-1>', self.getMousePos)
        self.frame.grid(row=row, column=column, columnspan=6)

    def getMousePos(self, event):
        print(self.frameNum)
        if self.manualVARMode:
            self.mouseX = event.x
            self.mouseY = event.y

    def endManualVAR(self, event):
        self.manualVARMode = False
