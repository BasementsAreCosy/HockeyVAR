import copy
import math
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
        self.zoom = 1
        self.frameJump = frameJump  # How many frames are displayed e.g: frameJump = 2, only frame 0, 2, 4, 6 will play
        self.fps = 30  # Video FPS, redefined when a video is submitted. 30 is standard?
        self.size = (750, 500)
        self.scrollX = self.size[0]/2
        self.scrollY = self.size[1]/2
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
        self.VARStage = [0, 'left']
        self.endStage = 5
        self.ballHistory = []
        self.ballCollisionPos = None

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
                    cv2.imwrite(f'footage/{count}-predval.jpg', image)  # Creates frame file, form orderSequence-modelConfidence
                count += 1
            except:
                print('End of video?')

    def displayFrames(self): # ONLY INVOKE AS THREAD
        comparisonFrameDifference = 12
        self.nextFrameDisplayTime = time.time()
        clickLocation = None
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
                    self.VARStage = [0, 'left']
                    self.manualVARMode = True
                    self.frameNum -= comparisonFrameDifference/2
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.VARInstructionLabel = tk.Label(self.root, text=f'Please select the {self.VARStage[1]}-most point of the ball.')
                    self.VARInstructionLabel.grid(row=0, column=1)
                    self.displayImageInFrame(1, 0, frameName=frameName)
                elif utils.roundToNearest(self.frameNum + self.frameJump, self.frameJump) <= self.lastFrame:
                    self.frameNum += self.frameJump
                else:  # End of video
                    self.displayImageInFrame(1, 0, frameName=frameName)
                    self.isPaused = True
            if self.manualVARMode:
                print(self.scrollX, self.scrollY, end=' | ')
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
                                    if utils.extractConfidenceVal(frameName) != 0:
                                        self.ballCollisionPos = self.ballHistory[-1][1]
                        self.VARInstructionLabel = tk.Label(self.root,
                                                            text=f'Please select the {self.VARStage[1]}-most point of the ball.')
                        self.VARInstructionLabel.grid(row=0, column=1)
                else:
                    self.VARInstructionLabel.destroy()
                    self.manualVARMode = False
                    if self.frameNum + self.frameJump <= self.lastFrame:
                        self.frameNum += comparisonFrameDifference
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.displayImageInFrame(1, 0, frameName=frameName)

    def displayVARImage(self, frameName):
        image = cv2.imread(frameName)
        for pos in self.ballHistory:
            cv2.circle(img=image, center=pos[1], radius=pos[2], color=(0, 255, 0), thickness=3)
        self.displayImageInFrame(1, 0, image=image)

    def displayImageInFrame(self, row, column, frameName=None, image=None):
        if frameName != None:
            image = cv2.imread(frameName)
            self.frame.configure(bg='green' if utils.extractConfidenceVal(frameName) == 0 else 'red')
        else:
            self.frame.configure(bg='red')
        image = self.zoomImage(image)
        frameImg = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
        if self.lastImage != None:
            self.lastImage.destroy()
        if self.currentImage != None:
            self.lastImage = self.currentImage
        self.currentImage = tk.Label(self.frame, image=frameImg)
        self.currentImage.image = frameImg
        self.currentImage.grid(row=0, column=0, padx=5, pady=5)
        self.currentImage.bind('<Button-1>', self.getMousePos)
        self.currentImage.bind('<MouseWheel>', self.scrollEvent)
        self.frame.grid(row=row, column=column, columnspan=6)

    def getMousePos(self, event):
        print(self.frameNum)
        if self.manualVARMode:
            #[i / 2 for i in image.shape[:-1]] if coord is None else coord[::-1]
            self.mouseX = round((event.x/self.zoom)+self.topLeftX)
            self.mouseY = round((event.y/self.zoom)+self.topLeftY)

    def scrollEvent(self, event):
        self.scrollX += (event.delta/120)*(event.x-self.size[0]/2)/self.zoom
        self.scrollY += (event.delta/120)*(event.y-self.size[1]/2)/self.zoom
        self.zoom = max(1, self.zoom + (event.delta/600))

    def zoomImage(self, image, angle=0):
        coord = None if self.scrollX == None or self.scrollY == None else (self.scrollX, self.scrollY)
        cy, cx = [i / 2 for i in image.shape[:-1]] if coord is None else coord[::-1]

        rot_mat = cv2.getRotationMatrix2D((cx, cy), angle, self.zoom)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)

        return result

    def endManualVAR(self, event):
        self.manualVARMode = False