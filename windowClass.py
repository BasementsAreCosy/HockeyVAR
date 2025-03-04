import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import utils
import videoClass
import peopleClasses
from tkinter import filedialog as fd
import threading
import time


class menuWindow:
    def __init__(self, conn, cursor):
        self.root = tk.Tk()
        self.root.minsize(250, 300)
        self.conn = conn
        self.cursor = cursor
        self.club = tk.StringVar()
        self.club.set('Select/Enter Your Club')
        self.team = tk.StringVar()
        self.team.set('Select/Enter Your Team')
        self.email = tk.StringVar()
        self.fName = tk.StringVar()
        self.lName = tk.StringVar()
        self.dob = tk.StringVar()
        self.isUmpire = tk.BooleanVar()
        self.password = tk.StringVar()
        self.club.trace_add('write', self.onClubChange)

        self.club1 = tk.StringVar()
        self.club1.set('Select/Enter Your Club')
        self.team1 = tk.StringVar()
        self.team1.set('Select/Enter Your Team')
        self.club1.trace_add('write', self.onClub1Change)

        self.club2 = tk.StringVar()
        self.club2.set('Select/Enter The Opposition Club')
        self.team2 = tk.StringVar()
        self.team2.set('Select/Enter The Opposition Team')
        self.club2.trace_add('write', self.onClub2Change)

        self.createWindow()

    def createWindow(self):
        self.loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)
        self.loginButton.grid(row=0, column=0, pady=2)

        self.signUpButton = tk.Button(self.root, text='Sign Up', command=self.showSignUpFields)
        self.signUpButton.grid(row=0, column=1, pady=2)

        self.lookupButton = tk.Button(self.root, text='Lookup Player', command=self.showLookupFields)
        self.lookupButton.grid(row=0, column=2, pady=2)

        self.root.mainloop()

    def showLoginFields(self):
        self.clearLoginWindow()

        self.loginLabel = tk.Label(self.root, text='Log In', justify='center')
        self.loginLabel.grid(row=0, column=0, columnspan=2, pady=2)

        self.emailLabel = tk.Label(self.root, text='Email:', justify='right')
        self.emailLabel.grid(row=1, column=0, pady=2)
        self.emailEntry = tk.Entry(self.root, textvariable=self.email)
        self.emailEntry.grid(row=1, column=1, pady=2)

        self.passwordLabel = tk.Label(self.root, text='Password:', justify='right')
        self.passwordLabel.grid(row=2, column=0, pady=2)
        self.passwordEntry = tk.Entry(self.root, textvariable=self.password, show='*')
        self.passwordEntry.grid(row=2, column=1, pady=2)

        self.hockeyWindowButton = tk.Button(self.root, text='Log In', command=self.submitLogin)
        self.hockeyWindowButton.grid(row=3, column=1, pady=2)

        self.signUpButton = tk.Button(self.root, text='Sign Up', command=self.showSignUpFields)
        self.signUpButton.grid(row=3, column=2, pady=2)

    def showSignUpFields(self):
        self.clearLoginWindow()

        self.signUpLabel = tk.Label(self.root, text='Sign Up', justify='center')
        self.signUpLabel.grid(row=0, column=0, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Clubs;''')
        clubs = self.cursor.fetchall()

        self.clubDropDown = ttk.Combobox(self.root, textvariable=self.club, values=[club[0] for club in clubs])
        self.clubDropDown.grid(row=1, column=1, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Teams;''')
        teams = self.cursor.fetchall()

        self.teamDropDown = ttk.Combobox(self.root, textvariable=self.team, values=[team[0] for team in teams])
        self.teamDropDown.grid(row=2, column=1, columnspan=2, pady=2)

        self.emailLabel = tk.Label(self.root, text='Email:', justify='right')
        self.emailLabel.grid(row=3, column=0, pady=2)
        self.emailEntry = tk.Entry(self.root, textvariable=self.email)
        self.emailEntry.grid(row=3, column=1, pady=2)

        self.fNameLabel = tk.Label(self.root, text='First Name:', justify='right')
        self.fNameLabel.grid(row=4, column=0, pady=2)
        self.fNameEntry = tk.Entry(self.root, textvariable=self.fName)
        self.fNameEntry.grid(row=4, column=1, pady=2)

        self.lNameLabel = tk.Label(self.root, text='Last Name:', justify='right')
        self.lNameLabel.grid(row=5, column=0, pady=2)
        self.lNameEntry = tk.Entry(self.root, textvariable=self.lName)
        self.lNameEntry.grid(row=5, column=1, pady=2)

        self.dobLabel = tk.Label(self.root, text='Date Of Birth:', justify='right')
        self.dobLabel.grid(row=6, column=0, pady=2)
        self.dobEntry = DateEntry(self.root, textvariable=self.dob)
        self.dobEntry.grid(row=6, column=1, pady=2)

        self.umpireLabel = tk.Label(self.root, text='Are you an umpire?', justify='right')
        self.umpireLabel.grid(row=7, column=0, pady=2)
        self.umpireEntry = tk.Checkbutton(self.root, variable=self.isUmpire)
        self.umpireEntry.grid(row=7, column=1, pady=2)

        self.passwordLabel = tk.Label(self.root, text='Password:', justify='right')
        self.passwordLabel.grid(row=8, column=0, pady=2)
        self.passwordEntry = tk.Entry(self.root, textvariable=self.password, show='*')
        self.passwordEntry.grid(row=8, column=1, pady=2)

        self.hockeyWindowButton = tk.Button(self.root, text='Sign Up', command=self.submitSignUp)
        self.hockeyWindowButton.grid(row=9, column=1, pady=2)

        self.loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)
        self.loginButton.grid(row=9, column=2, pady=2)

    def showLookupFields(self):
        self.clearLoginWindow()

        self.lookupLabel = tk.Label(self.root, text='Look-Up', justify='center')
        self.lookupLabel.grid(row=0, column=0, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Clubs;''')
        clubs = self.cursor.fetchall()

        self.clubDropDown = ttk.Combobox(self.root, textvariable=self.club, values=[club[0] for club in clubs])
        self.clubDropDown.grid(row=1, column=1, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Teams;''')
        teams = self.cursor.fetchall()

        self.teamDropDown = ttk.Combobox(self.root, textvariable=self.team, values=[team[0] for team in teams])
        self.teamDropDown.grid(row=2, column=1, columnspan=2, pady=2)

        self.fNameLabel = tk.Label(self.root, text='First Name:', justify='right')
        self.fNameLabel.grid(row=4, column=0, pady=2)
        self.fNameEntry = tk.Entry(self.root, textvariable=self.fName)
        self.fNameEntry.grid(row=4, column=1, pady=2)

        self.lNameLabel = tk.Label(self.root, text='Last Name:', justify='right')
        self.lNameLabel.grid(row=5, column=0, pady=2)
        self.lNameEntry = tk.Entry(self.root, textvariable=self.lName)
        self.lNameEntry.grid(row=5, column=1, pady=2)

        self.dobLabel = tk.Label(self.root, text='Date Of Birth:', justify='right')
        self.dobLabel.grid(row=6, column=0, pady=2)
        self.dobEntry = DateEntry(self.root, textvariable=self.dob)
        self.dobEntry.grid(row=6, column=1, pady=2)

        self.hockeyWindowButton = tk.Button(self.root, text='Look-Up', command=self.submitLookup)
        self.hockeyWindowButton.grid(row=9, column=1, pady=2)

        self.signUpButton = tk.Button(self.root, text='Sign Up', command=self.showSignUpFields)
        self.signUpButton.grid(row=9, column=2, pady=2)

        self.loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)
        self.loginButton.grid(row=9, column=3, pady=2)

    def showMatchFields(self):
        self.clearLoginWindow()

        self.matchLabel = tk.Label(self.root, text='Match details', justify='center')
        self.matchLabel.grid(row=0, column=0, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Clubs;''')
        clubs = self.cursor.fetchall()

        self.club1DropDown = ttk.Combobox(self.root, textvariable=self.club1, values=[club[0] for club in clubs])
        self.club1DropDown.grid(row=1, column=1, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Teams;''')
        teams = self.cursor.fetchall()

        self.team1DropDown = ttk.Combobox(self.root, textvariable=self.team1, values=[team[0] for team in teams])
        self.team1DropDown.grid(row=2, column=1, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Clubs;''')
        clubs = self.cursor.fetchall()

        self.club2DropDown = ttk.Combobox(self.root, textvariable=self.club2, values=[club[0] for club in clubs])
        self.club2DropDown.grid(row=1, column=1, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Teams;''')
        teams = self.cursor.fetchall()

        self.team2DropDown = ttk.Combobox(self.root, textvariable=self.team2, values=[team[0] for team in teams])
        self.team2DropDown.grid(row=2, column=1, columnspan=2, pady=2)

        self.fNameLabel = tk.Label(self.root, text='Umpire First Name:', justify='right')
        self.fNameLabel.grid(row=4, column=0, pady=2)
        self.fNameEntry = tk.Entry(self.root, textvariable=self.fName)
        self.fNameEntry.grid(row=4, column=1, pady=2)

        self.lNameLabel = tk.Label(self.root, text='Umpire Last Name:', justify='right')
        self.lNameLabel.grid(row=5, column=0, pady=2)
        self.lNameEntry = tk.Entry(self.root, textvariable=self.lName)
        self.lNameEntry.grid(row=5, column=1, pady=2)

        self.hockeyWindowButton = tk.Button(self.root, text='Continue', command=self.submitMatch)
        self.hockeyWindowButton.grid(row=9, column=1, pady=2)

        self.loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)
        self.loginButton.grid(row=9, column=2, pady=2)

    def submitSignUp(self):
        if self.email.get() != '' and self.fName.get() != '' and self.lName.get() != '' and self.password.get() != '' and self.club.get() != '' and self.club.get() != 'Select/Enter Your Club' and self.team.get() != 'Select/Enter Your Team':
            self.clearLoginWindow()
            if self.isUmpire.get():
                self.showLookupFields()
            else:
                self.openHockeyWindow(peopleClasses.Player())

            self.cursor.execute('''INSERT OR IGNORE INTO Clubs (name) VALUES (?);''', (self.club.get(),))
            self.cursor.execute('''SELECT ID FROM Clubs WHERE name = ?;''', (self.club.get(),))
            self.cursor.execute(
                '''INSERT OR IGNORE INTO Teams (club_id, name, challenges, successful_challenges) VALUES (?, ?, ?, ?);''',
                (self.cursor.fetchone()[0], self.team.get(), 0, 0))
            self.cursor.execute('''SELECT ID FROM Teams WHERE name = ?;''', (self.team.get(),))
            self.cursor.execute(
                '''INSERT OR IGNORE INTO people (email, first_name, last_name, date_of_birth, team, is_umpire, password) VALUES (?, ?, ?, ?, ?, ?, ?);''',
                (self.email.get(), self.fName.get(), self.lName.get(), self.dob.get(), self.cursor.fetchone()[0], self.isUmpire.get(),
                 self.password.get()))
        else:
            self.badDetails = tk.Label(self.root,
                                       text='Your details are not formatted correctly.\nMake sure each field has a value\nand your team is selected from the drop down.',
                                       fg='red')
            self.badDetails.grid(row=10, column=0, columnspan=2, pady=2)

    def submitLogin(self):
        self.cursor.execute('''SELECT * FROM People WHERE email = ? AND password = ?;''', (self.email.get(), self.password.get()))
        results = self.cursor.fetchall()
        if results != []:
            self.clearLoginWindow()
            if results[0][6]:
                self.showLookupFields()
            else:
                self.openHockeyWindow(peopleClasses.Player())
        else:
            self.badDetails = tk.Label(self.root, text='The details you have provided do not match an account.', fg='red')
            self.badDetails.grid(row=4, column=0, columnspan=2, pady=2)

    def submitLookup(self):
        self.cursor.execute('''SELECT * FROM People WHERE club = ? AND team = ? AND f_name = ? AND l_name = ? AND dob = ?;''',
                            (self.club.get(), self.team.get(), self.fName.get(), self.lName.get(), self.dob.get()))
        results = self.cursor.fetchall()
        if results != []:
            self.clearLoginWindow()
            self.openHockeyWindow(peopleClasses.Umpire())
        else:
            self.badDetails = tk.Label(self.root, text='The details you have provided do not match an account.',
                                       fg='red')
            self.badDetails.grid(row=4, column=0, columnspan=2, pady=2)

    def onClubChange(self, *args):
        self.cursor.execute('''SELECT * FROM Clubs WHERE name LIKE ?''', (self.club.get() + '%',))
        clubs = self.cursor.fetchall()
        teams = []
        if clubs != []:
            placeholders = ', '.join('?' for club in clubs)
            self.cursor.execute(f'''SELECT name FROM Teams WHERE club_id IN ({placeholders});''',
                                [club[0] for club in clubs])
            teams = self.cursor.fetchall()
        self.clubDropDown['values'] = [club[1] for club in clubs]
        self.teamDropDown['values'] = [team[0] for team in teams]

    def onClub1Change(self, *args):
        self.cursor.execute('''SELECT * FROM Clubs WHERE name LIKE ?''', (self.club1.get() + '%',))
        clubs = self.cursor.fetchall()
        teams = []
        if clubs != []:
            placeholders = ', '.join('?' for club in clubs)
            self.cursor.execute(f'''SELECT name FROM Teams WHERE club_id IN ({placeholders});''',
                                [club[0] for club in clubs])
            teams = self.cursor.fetchall()
        self.club1DropDown['values'] = [club[1] for club in clubs]
        self.team1DropDown['values'] = [team[0] for team in teams]

    def onClub2Change(self, *args):
        self.cursor.execute('''SELECT * FROM Clubs WHERE name LIKE ?''', (self.club2.get() + '%',))
        clubs = self.cursor.fetchall()
        teams = []
        if clubs != []:
            placeholders = ', '.join('?' for club in clubs)
            self.cursor.execute(f'''SELECT name FROM Teams WHERE club_id IN ({placeholders});''',
                                [club[0] for club in clubs])
            teams = self.cursor.fetchall()
        self.club2DropDown['values'] = [club[1] for club in clubs]
        self.team2DropDown['values'] = [team[0] for team in teams]

    def selectChallenger(self):
        pass  # Select a challenger (almost identical to sign up/log in page) so that challenges can be aggregated

    def openHockeyWindow(self, user):
        self.cursor.execute('''INSERT OR IGNORE INTO Matches (home_team, away_team, umpire) VALUES (?, ?, ?);''')
        hockeyTkinterWindow(user, root=self.root)

    def clearLoginWindow(self):
        for widget in self.root.winfo_children():
            widget.destroy()


class hockeyTkinterWindow:
    def __init__(self, user, root=None):
        self.frameControlFlag = 0  # -1 for rewinding, 1 for forwarding, 0 for all else
        self.video = None
        self.user = user
        if root != None:
            self.createWindow(root=root)
        else:
            self.createWindow()

    def createWindow(self, root=None):
        if root == None:
            self.root = tk.Tk()
            self.root.minsize(250, 300)
        else:
            self.root = root

        self.mouseX = 0
        self.mouseY = 0

        self.submitVideoButton = tk.Button(self.root, text='Submit File', command=self.submitVideo,
                                           activebackground='blue', activeforeground='white')
        self.submitVideoButton.grid(row=0, column=0, pady=2)

        self.root.after(500, self.frameControlLoop)

    def createButtonsWidget(self):
        self.buttonFrame = tk.Frame(self.root, bg='grey')
        self.buttonFrame.grid(row=3, column=0, columnspan=6)

        self.reverseImage = utils.openImageResize('buttonImages/back.png', (20, 20))
        self.reverseButton = tk.Button(self.buttonFrame, image=self.reverseImage, activebackground='blue',
                                       activeforeground='white')
        self.reverseButton.bind('<ButtonPress-1>', self.reverseFrame)
        self.reverseButton.bind('<ButtonRelease-1>', self.stopFrameControl)
        self.reverseButton.grid(row=0, column=0, padx=5, pady=2)

        self.playImage = utils.openImageResize('buttonImages/play.png', (20, 20))
        self.playButton = tk.Button(self.buttonFrame, image=self.playImage, command=self.playVideo,
                                    activebackground='blue',
                                    activeforeground='white')
        self.playButton.grid(row=0, column=1, padx=5, pady=2)

        self.pauseImage = utils.openImageResize('buttonImages/pause.png', (20, 20))
        self.pauseButton = tk.Button(self.buttonFrame, image=self.pauseImage, command=self.pauseVideo,
                                     activebackground='blue',
                                     activeforeground='white')
        self.pauseButton.grid(row=0, column=2, padx=5, pady=2)

        self.forwardImage = utils.openImageResize('buttonImages/forward.png', (20, 20))
        self.forwardButton = tk.Button(self.buttonFrame, image=self.forwardImage, activebackground='blue',
                                       activeforeground='white')
        self.forwardButton.bind('<ButtonPress-1>', self.forwardFrame)
        self.forwardButton.bind('<ButtonRelease-1>', self.stopFrameControl)
        self.forwardButton.grid(row=0, column=3, padx=5, pady=2)

        self.slowImage = utils.openImageResize('buttonImages/halfspeed.png', (20, 20))
        self.slowButton = tk.Button(self.buttonFrame, image=self.slowImage, command=self.halfSpeed,
                                    activebackground='blue',
                                    activeforeground='white')
        self.slowButton.grid(row=0, column=4, padx=5, pady=2)

        self.normalImage = utils.openImageResize('buttonImages/normalspeed.png', (20, 20))
        self.normalButton = tk.Button(self.buttonFrame, image=self.normalImage, command=self.normalSpeed,
                                      activebackground='blue',
                                      activeforeground='white')
        self.normalButton.grid(row=0, column=5, padx=5, pady=2)

        self.challengeImage = utils.openImageResize('buttonImages/challenge.png', (20, 20))
        self.challengeButton = tk.Button(self.buttonFrame, image=self.challengeImage, command=self.challenge,
                                         activebackground='blue',
                                         activeforeground='white')
        self.challengeButton.grid(row=0, column=6, padx=5, pady=2)

    def frameControlLoop(self):
        if self.frameControlFlag != 0:
            if self.frameControlFlag == 1 and self.video.frameNum + self.video.frameJump <= self.video.lastFrame:
                self.video.frameNum += self.video.frameJump

            if self.frameControlFlag == -1 and self.video.frameNum - self.video.frameJump >= 0:
                self.video.frameNum -= self.video.frameJump

            self.video.nextFrameDisplayTime = time.time()

        try:
            self.root.after(self.video.frameJump * 200, self.frameControlLoop)
        except:
            self.root.after(200, self.frameControlLoop)

    def submitVideo(self):
        try:
            self.video.videoEnded = True
        except:
            print('no video')
        submitVideoThread = threading.Thread(target=self.processVideo)
        submitVideoThread.start()

    def processVideo(self):
        frameJump = 1
        filename = fd.askopenfilename()
        self.video = videoClass.HockeyVideo(self.root, filename, frameJump=frameJump, debug=True)
        displayThread = threading.Thread(target=self.video.displayFrames)
        displayThread.start()
        self.createButtonsWidget()

    def getMousePos(self, event):
        self.mouseX = event.x
        self.mouseY = event.y
        print(self.mouseX, self.mouseY)

    def normalSpeed(self):
        self.video.speed = 1
        self.video.nextFrameDisplayTime = time.time()

    def halfSpeed(self):
        self.video.speed = 0.3
        self.video.nextFrameDisplayTime = time.time()

    def pauseVideo(self):
        self.video.isPaused = True

    def playVideo(self):
        self.video.isPaused = False
        self.video.nextFrameDisplayTime = time.time()

    def reverseFrame(self, event):
        self.pauseVideo()
        self.frameControlFlag = -1
        if self.video.frameNum - self.video.frameJump >= 0:
            self.video.frameNum -= self.video.frameJump

    def forwardFrame(self, event):
        self.pauseVideo()
        self.frameControlFlag = 1
        if self.video.frameNum + self.video.frameJump <= self.video.lastFrame:
            self.video.frameNum += self.video.frameJump

    def stopFrameControl(self, event):
        self.frameControlFlag = 0

    def challenge(self):
        self.video.footIdentified = True
        self.video.isPaused = False