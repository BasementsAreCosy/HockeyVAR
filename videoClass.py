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
    def __init__(self, root, path, frameJump=1):
        # CONSTANTS - Python doesn't support this natively
        self.root = root  # Tkinter window
        self.root.bind('<Escape>', self.endManualVAR)  # Cancels challenge initiation
        self.path = path  # Video path
        self.footagePath = '/'.join(self.path.split('/')[:-1])  # Removes video path
        self.footagePath = self.footagePath + '/footage'  # Adds footage directory to path
        self.frame = tk.Frame(self.root, bg='green')  # Initialise the tkinter frame which holds the video
        self.challengeCorrect = None  # Used to update the database
        self.footIdentified = False  # Used as a flag in the window with this class as an attribute
        self.lastImage = None  # Store of the last image to prevent flashing in between frames
        self.currentImage = None  # Store of current image
        self.mouseX = None  # Used for bounding box
        self.mouseY = None  # Used for bounding box
        self.previewX = None  # Used for bounding box
        self.previewY = None  # Used for bounding box
        self.boundingBox = {'topLeft': None, 'width': None, 'height': None}  # Bounding box data
        self.scale = 1  # Used to zoom in on the bounding box created
        self.frameJump = frameJump  # How many frames are displayed e.g: frameJump = 2, only frame 0, 2, 4, 6 will play
        self.fps = 30  # Video FPS, redefined when a video is submitted. 30 is standard?
        self.size = (750, 500)  # Size of image
        self.separateFrames()  # Turns the video into a sequence of frames
        self.frames = glob.glob(f'{self.footagePath}/*')  # Creates a list of frame paths - queue structure
        self.frames.sort(key=utils.extractFrameNum)  # Sorts into order
        self.lastFrame = utils.extractFrameNum(self.frames[-1])  # path of the last frame - end of queue pointer
        self.frameNum = 0  # Current frame being displayed - front of queue pointer
        self.nextFrameDisplayTime = time.time()  # Time when the next frame should display
        self.speed = 1  # Playback speed
        self.isPaused = False  # Flag for pausing
        self.videoEnded = False  # Ends video threading when True
        self.manualVARMode = False  # Flag to loop the manualVAR function
        self.VARStage = [0, 'left']  # Indicates which part of the ball is being clicked in which frame relative to the start of VAR
        self.endStage = 5  # Number of frames used in the VAR
        self.ballHistory = []  # Stores the position of the ball at each stage in VAR
        self.ballCollisionIndex = None  # Stores the frame number of the collision

    def separateFrames(self):
        files = glob.glob(f'{self.footagePath}/*')
        for f in files:
            os.remove(f)  # Clears frame directory

        vidObj = cv2.VideoCapture(self.path)
        self.fps = vidObj.get(cv2.CAP_PROP_FPS)

        count = 0
        success = 1
        while success:  # While there are remaining frames
            try:
                success, image = vidObj.read()  # Get image
                if count % self.frameJump == 0:  # If it is not a skipped frame for performance
                    image = cv2.resize(image, self.size, interpolation=cv2.INTER_CUBIC)
                    cv2.imwrite(f'{self.footagePath}/{count}.jpg', image)  # Creates frame file, name = frame number
                count += 1
            except:
                print('End of video.')

    def displayFrames(self):  # ONLY INVOKE AS THREAD
        comparisonFrameDifference = 10  # Frame jump between each VAR frame
        self.nextFrameDisplayTime = time.time()  # Sets the current time as when the next frame should be displayed
        while True:  # Thread: so while video exists, this always runs
            if self.videoEnded:
                return  # When returned, the thread ends
            if not self.manualVARMode:
                frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]  # Gets the path of the current frame
                self.displayImageInFrame(1, 0, frameName=frameName)
                while self.speed == 0 or self.isPaused:
                    if self.videoEnded:
                        return  # When returned, the thread ends
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.displayImageInFrame(1, 0, frameName=frameName)

                self.nextFrameDisplayTime += (self.frameJump/self.fps)/self.speed  # Sets the time of the next frame to be displayed
                if self.nextFrameDisplayTime - time.time() >= 0:  # Wait until time to show next frame
                    time.sleep(self.nextFrameDisplayTime - time.time())
                if self.footIdentified:
                    self.footIdentified = False
                    time.sleep(1)  # Stutter frame when foot identified
                    self.VARStage[1] = 'left'  # Ensure it is started at the left of the ball
                    self.manualVARMode = True  # Start manualVAR loop
                    self.mouseX = None  # Allow new ball locations to be stored
                    self.mouseY = None
                    self.frameNum -= comparisonFrameDifference/2  # Reverse to first VAR frame
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]  # Gets frame path
                    self.VARInstructionLabel = tk.Label(self.root, text=f'Please select the {self.VARStage[1]}-most point of the ball.')
                    self.VARInstructionLabel.grid(row=0, column=3)
                    self.displayImageInFrame(1, 0, frameName=frameName)
                elif utils.roundToNearest(self.frameNum + self.frameJump, self.frameJump) <= self.lastFrame:  # If not the end of video
                    self.frameNum += self.frameJump  # Next frame
                else:  # End of video
                    self.displayImageInFrame(1, 0, frameName=frameName)  # Display last frame
                    self.isPaused = True  # Start pause loop by setting flag
            if self.manualVARMode:  # Manual VAR loop
                if self.VARStage[0] < self.endStage:  # If we haven't reached the end of VAR
                    self.displayVARImage(frameName)  # Displays current frame in VAR
                    if self.mouseX != None and self.mouseY != None:
                        if self.VARStage[1] == 'left':
                            clickLocation = (self.mouseX, self.mouseY)  # Store left-most ball position
                            self.mouseX = None  # Reset mouse pos
                            self.mouseY = None
                            self.VARStage[1] = 'right'  # Moves to the right of the ball
                        elif self.VARStage[1] == 'right':
                            self.ballHistory.append((self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump], ((clickLocation[0]+self.mouseX)//2, self.mouseY), abs(self.mouseX-clickLocation[0])//2))  # Add ball location to ballHistory
                            frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                            self.mouseX = None
                            self.mouseY = None
                            self.VARStage[0] += 1  # Next frame
                            self.VARStage[1] = 'left'
                            while frameName == self.ballHistory[-1][0] or frameName == None:  # Ensures next frame
                                if utils.roundToNearest(self.frameNum + comparisonFrameDifference/self.endStage, self.frameJump) <= self.lastFrame:
                                    self.frameNum += comparisonFrameDifference/self.endStage
                                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                        self.VARInstructionLabel = tk.Label(self.root,
                                                            text=f'Please select the {self.VARStage[1]}-most point of the ball.')
                        self.VARInstructionLabel.grid(row=0, column=3)
                else:  # VAR ended
                    self.displayVARResult()  # Display ball history + vectors showing change in direction
                    self.ballHistory = []  # Resets VAR variables
                    self.ballCollisionIndex = None
                    self.VARStage[0] = 0
                    self.endVARPositiveButton = tk.Button(self.root, text='Challenger Correct', command=self.correctChallenge)
                    self.endVARPositiveButton.grid(row=0, column=1)
                    self.endVARNegativeButton = tk.Button(self.root, text='Challenger Incorrect', command=self.incorrectChallenge)
                    self.endVARNegativeButton.grid(row=0, column=2)
                    while self.manualVARMode:  # Wait for user to identify (in)correct challenge
                        pass
                    self.endVARPositiveButton.destroy()  # Remove buttons and labels
                    self.endVARNegativeButton.destroy()
                    self.VARInstructionLabel.destroy()
                    if self.frameNum + self.frameJump <= self.lastFrame:
                        self.frameNum += comparisonFrameDifference  # Next frame
                    self.nextFrameDisplayTime = time.time()
                    frameName = self.frames[utils.roundToNearest(self.frameNum, self.frameJump)//self.frameJump]
                    self.displayImageInFrame(1, 0, frameName=frameName)

    def displayVARResult(self):
        self.boundingBox = {'topLeft': None, 'width': None, 'height': None}  # Reset zooming box
        pointsBeforeCollision = []  # Initialise variables
        pointsAfterCollision = []
        vectors = []
        angles = []
        averageAngle = 0
        postCollisionIndexes = []
        for i in range(len(self.ballHistory) - 1):  # Loop adds vectors between ball positions to a list
            vectors.append((self.ballHistory[i + 1][1][0] - self.ballHistory[i][1][0], self.ballHistory[i + 1][1][1] - self.ballHistory[i][1][1]))
        for i in range(len(vectors)-1):  # Loop adds each angle between ball movements to a list
            angles.append(utils.getVectorAngle(vectors[i], vectors[i+1]))
            if utils.vectorWithinTolerance(averageAngle, angles[-1], math.pi / 8):  # If ball has not changed direction
                averageAngle = utils.listMean(angles)  # Change the average angle to reflect all the vectors before change in direction
            else:  # If ball has changed direction
                angles.pop(-1)  # Remove the change in direction from the lsit of angles
                postCollisionIndexes.append(i)  # Add this index to the change in direction
        if postCollisionIndexes != []:  # Find the index of collision
            collisionIndex = min(postCollisionIndexes) + 1
        else:  # If no collision, set collision to the end so only 1 vector is shown
            collisionIndex = self.endStage - 1
        image = cv2.imread(self.ballHistory[collisionIndex][0])  # Get the frame of collision
        for i in range(len(self.ballHistory)):
            if i < collisionIndex:
                pointsBeforeCollision.append(self.ballHistory[i][1])  # Add all points before collision
                colour = (0, 255, 0)
            elif i == collisionIndex:
                colour = (0, 127, 255)  # Add point of collision
            else:
                pointsAfterCollision.append(self.ballHistory[i][1])  # Add all points after collision
                colour = (0, 0, 255)
            cv2.circle(img=image, center=self.ballHistory[i][1], radius=self.ballHistory[i][2], color=colour, thickness=1)  # Create circle for the ball with appropriate colour indication
        cv2.line(img=image, pt1=self.ballHistory[collisionIndex][1],
                 pt2=utils.avgPoint(pointsBeforeCollision),
                 color=(0, 255, 0), thickness=2)  # Create line for before the collision
        if postCollisionIndexes != []:  # If collision occured
            cv2.line(img=image, pt1=self.ballHistory[collisionIndex][1],
                     pt2=utils.avgPoint(pointsAfterCollision),
                     color=(0, 0, 255), thickness=2)  # Create line for after the collision
        self.displayImageInFrame(1, 0, image=image)  # Display final image with vectors and ball history

    def displayVARImage(self, frameName):
        image = cv2.imread(frameName)
        for pos in self.ballHistory:
            cv2.circle(img=image, center=pos[1], radius=pos[2], color=(0, 255, 0), thickness=2)  # Display the current ball history
        self.displayImageInFrame(1, 0, image=image)

    def displayImageInFrame(self, row, column, frameName=None, image=None):
        if frameName != None:
            image = cv2.imread(frameName)  # Open image
            self.frame.configure(bg='green' if not self.footIdentified else 'red')  # Red for when VAR is active
        else:
            self.frame.configure(bg='red')
        if self.boundingBox['topLeft'] != None and self.boundingBox['width'] != None and self.boundingBox['height'] != None:
            image = image[self.boundingBox['topLeft'][1]:self.boundingBox['topLeft'][1]+self.boundingBox['height'], self.boundingBox['topLeft'][0]:self.boundingBox['topLeft'][0]+self.boundingBox['width']]  # Crop image to bounding box
            image = self.zoomOnBoundingBox(image)  # Zoom on cropped image
        elif self.boundingBox['topLeft'] != None:
            topLeft, bottomRight = utils.getValidRange(self.boundingBox['topLeft'], (self.previewX, self.previewY))  # Ensure top left and bottom right in correct format
            previewBox = image[topLeft[1]:bottomRight[1], topLeft[0]:bottomRight[0]]  # Shows the preview of bounding box
            previewBox = np.clip(previewBox + 50, 0, 255)  # Adds 50 to every colour RGB value to make it lighter, capping at 255
            image[topLeft[1]:bottomRight[1], topLeft[0]:bottomRight[0]] = previewBox  # Replace current bounding box range in image with the preview
        frameImg = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))  # Convert to be displayed in tkinter
        if self.lastImage != None:  # If last image exists behind current image
            self.lastImage.destroy()  # Destroy last image behind image
        if self.currentImage != None:  # If current image exists
            self.lastImage = self.currentImage  # Set this to the last image to be displayed behind the current image to prevent flashing
        self.currentImage = tk.Label(self.frame, image=frameImg)  # Create label with image
        self.currentImage.image = frameImg  # Reset label image to the image to prevent garbage collection when this image transfers to the last image
        self.currentImage.grid(row=0, column=0, padx=5, pady=5)  # Display image
        self.currentImage.bind('<Button-1>', self.getMouseBallPos)  # Bind left mosue button to returning the mouse position in relation to the image
        self.currentImage.bind('<Button-3>', self.createBoundingBox)  # Bind right mouse button to creating the bounding box used for zooming
        self.currentImage.bind('<Motion>', self.getMousePreviewBox)  # Bind mouse motion to constantly update the preview box for zooming
        self.frame.grid(row=row, column=column, columnspan=6)  # Display the grid

    def getMouseBallPos(self, event):
        if self.manualVARMode:  # Only used during VAR
            self.mouseX = event.x  # Get mouse pos
            self.mouseY = event.y
            if self.boundingBox['topLeft'] != None and self.boundingBox['width'] != None and self.boundingBox['height'] != None:  # If zoomed in on bounding box
                self.mouseX = round((self.mouseX/self.scale) + self.boundingBox['topLeft'][0])  # Translates mouse pos based on zoom
                self.mouseY = round((self.mouseY/self.scale) + self.boundingBox['topLeft'][1])

    def createBoundingBox(self, event):
        if self.boundingBox['topLeft'] == None:  # If no top left
            self.boundingBox['topLeft'] = [event.x, event.y]  # Set top left
        elif self.boundingBox['width'] == None or self.boundingBox['height'] == None:  # If there is a top left but no bottom left
            self.boundingBox['width'] = abs(event.x-self.boundingBox['topLeft'][0])  # Set width/height
            self.boundingBox['height'] = abs(event.y-self.boundingBox['topLeft'][1])
            if event.x < self.boundingBox['topLeft'][0]:
                self.boundingBox['topLeft'][0] = event.x  # Set new top left if bottom right is not underneath and to the right
            if event.y < self.boundingBox['topLeft'][1]:
                self.boundingBox['topLeft'][1] = event.y
        else:
            self.boundingBox = {'topLeft': None, 'width': None, 'height': None}  # If bounding box already exists, remove bounding box

    def getMousePreviewBox(self, event):
        self.previewX = event.x  # Get mouse pos
        self.previewY = event.y

    def zoomOnBoundingBox(self, image):
        height, width = image.shape[:2]  # Find image size
        self.scale = min(self.size[0] / width, self.size[1] / height)  # Find zoom
        image = cv2.resize(image, (0, 0), fx=self.scale, fy=self.scale)  # Resize zoomed image to enlarge
        return image

    def correctChallenge(self):
        self.challengeCorrect = True  # Sets challengeCorrect flag
        self.manualVARMode = False

    def incorrectChallenge(self):  # Sets challengeCorrect flag
        self.challengeCorrect = False
        self.manualVARMode = False

    def endManualVAR(self, event):  # Stop manualVARMode
        self.manualVARMode = False
