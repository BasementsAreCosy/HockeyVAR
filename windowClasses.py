import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import utils
import videoClass
import peopleClasses
from tkinter import filedialog as fd
import threading
import time
import datetime
import sqlite3


class menuWindow:
    def __init__(self):
        self.root = tk.Tk()  # Initialise tkinter root
        self.root.minsize(250, 300)  # Set minimum size of window
        self.conn = sqlite3.connect('hockey_video.db')  # Connect to the database
        self.cursor = self.conn.cursor()  # Set cursor as a separate variable

        self.tkClub = tk.StringVar()  # Create Fields as tkinter StringVars to allow getting/setting from tkinter Entry objects
        self.tkClub.set('Select/Enter Your Club')  # Set default text
        self.tkTeam = tk.StringVar()
        self.tkTeam.set('Select/Enter Your Team')
        self.tkEmail = tk.StringVar()
        self.tkFName = tk.StringVar()
        self.tkLName = tk.StringVar()
        self.tkDob = tk.StringVar()
        self.tkIsUmpire = tk.BooleanVar()  # Create as a boolean instead
        self.tkPassword = tk.StringVar()
        self.tkClub.trace_add('write', self.onClubChange)  # Every time the entry for the club changes, call function

        self.ID = None  # Initialise challenger variables
        self.challenger = None
        self.clubID = None
        self.teamID = None
        self.email = None
        self.fName = None
        self.lName = None
        self.dob = None
        self.isUmpire = None
        self.password = None
        self.challenges = None
        self.successfulChallenges = None

        self.tkClub1 = tk.StringVar()  # Initialise more fields + set default texts
        self.tkClub1.set('Select/Enter Your Club')
        self.tkTeam1 = tk.StringVar()
        self.tkTeam1.set('Select/Enter Your Team')
        self.tkClub1.trace_add('write', self.onClub1Change)

        self.tkClub2 = tk.StringVar()
        self.tkClub2.set('Select/Enter The Opposition Club')
        self.tkTeam2 = tk.StringVar()
        self.tkTeam2.set('Select/Enter The Opposition Team')
        self.tkClub2.trace_add('write', self.onClub2Change)

        self.userLoggedIn = False  # Is the challenger logged in -> True, else false

        self.createWindow()  # Calls fucntion to construct window

    def createWindow(self):  # Create a series of tkinter buttons associated to logging in
        self.loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)
        self.loginButton.grid(row=0, column=0, pady=2)

        self.signUpButton = tk.Button(self.root, text='Sign Up', command=self.showSignUpFields)
        self.signUpButton.grid(row=0, column=1, pady=2)

        self.lookupButton = tk.Button(self.root, text='Lookup Player', command=self.showLookupFields)
        self.lookupButton.grid(row=0, column=2, pady=2)

        self.root.mainloop()

    def showLoginFields(self):  # Displays login page with labels, buttons and entry fields
        self.clearLoginWindow()

        self.loginLabel = tk.Label(self.root, text='Log In', justify='center')
        self.loginLabel.grid(row=0, column=0, columnspan=2, pady=2)

        self.emailLabel = tk.Label(self.root, text='Email:', justify='right')
        self.emailLabel.grid(row=1, column=0, pady=2)
        self.emailEntry = tk.Entry(self.root, textvariable=self.tkEmail)
        self.emailEntry.grid(row=1, column=1, pady=2)

        self.passwordLabel = tk.Label(self.root, text='Password:', justify='right')
        self.passwordLabel.grid(row=2, column=0, pady=2)
        self.passwordEntry = tk.Entry(self.root, textvariable=self.tkPassword, show='*')  # show='*' to hide password
        self.passwordEntry.grid(row=2, column=1, pady=2)

        self.hockeyWindowButton = tk.Button(self.root, text='Log In', command=self.submitLogin)  # Button to progress to next page
        self.hockeyWindowButton.grid(row=3, column=1, pady=2)

        self.signUpButton = tk.Button(self.root, text='Sign Up', command=self.showSignUpFields)  # Button to go back to sign up
        self.signUpButton.grid(row=3, column=2, pady=2)

    def showSignUpFields(self):  # Displays sign up page with labels, buttons and entry fields
        self.clearLoginWindow()  # Clears the window

        self.signUpLabel = tk.Label(self.root, text='Sign Up', justify='center')
        self.signUpLabel.grid(row=0, column=0, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Clubs;''')  # Gets a list of existing clubs to sign up with
        clubs = self.cursor.fetchall()

        self.clubDropDown = ttk.Combobox(self.root, textvariable=self.tkClub, values=[club[0] for club in clubs])
        self.clubDropDown.grid(row=1, column=1, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Teams;''')  # Gets a list of teams to sign up with
        teams = self.cursor.fetchall()

        self.teamDropDown = ttk.Combobox(self.root, textvariable=self.tkTeam, values=[team[0] for team in teams])
        self.teamDropDown.grid(row=2, column=1, columnspan=2, pady=2)

        self.emailLabel = tk.Label(self.root, text='Email:', justify='right')
        self.emailLabel.grid(row=3, column=0, pady=2)
        self.emailEntry = tk.Entry(self.root, textvariable=self.tkEmail)
        self.emailEntry.grid(row=3, column=1, pady=2)

        self.fNameLabel = tk.Label(self.root, text='First Name:', justify='right')
        self.fNameLabel.grid(row=4, column=0, pady=2)
        self.fNameEntry = tk.Entry(self.root, textvariable=self.tkFName)
        self.fNameEntry.grid(row=4, column=1, pady=2)

        self.lNameLabel = tk.Label(self.root, text='Last Name:', justify='right')
        self.lNameLabel.grid(row=5, column=0, pady=2)
        self.lNameEntry = tk.Entry(self.root, textvariable=self.tkLName)
        self.lNameEntry.grid(row=5, column=1, pady=2)

        self.dobLabel = tk.Label(self.root, text='Date Of Birth:', justify='right')
        self.dobLabel.grid(row=6, column=0, pady=2)
        self.dobEntry = DateEntry(self.root, textvariable=self.tkDob, date_pattern='dd-mm-yyyy')  # Show calendar to choose date
        self.dobEntry.grid(row=6, column=1, pady=2)

        self.umpireLabel = tk.Label(self.root, text='Are you an umpire?', justify='right')
        self.umpireLabel.grid(row=7, column=0, pady=2)
        self.umpireEntry = tk.Checkbutton(self.root, variable=self.tkIsUmpire)
        self.umpireEntry.grid(row=7, column=1, pady=2)

        self.passwordLabel = tk.Label(self.root, text='Password:', justify='right')
        self.passwordLabel.grid(row=8, column=0, pady=2)
        self.passwordEntry = tk.Entry(self.root, textvariable=self.tkPassword, show='*')
        self.passwordEntry.grid(row=8, column=1, pady=2)

        self.hockeyWindowButton = tk.Button(self.root, text='Sign Up', command=self.submitSignUp)  # Submit sign up fields
        self.hockeyWindowButton.grid(row=9, column=1, pady=2)

        self.loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)  # Go back to log in
        self.loginButton.grid(row=9, column=2, pady=2)

    def showLookupFields(self, text='Look-Up'):  # Used to look up players stats and to look up players if they are a challenger
        self.clearLoginWindow()  # Clears window

        self.lookupLabel = tk.Label(self.root, text=text, justify='center')
        self.lookupLabel.grid(row=0, column=0, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Clubs;''')  # The following gets teams and clubs from the database for the user to select from a drop down
        clubs = self.cursor.fetchall()

        self.clubDropDown = ttk.Combobox(self.root, textvariable=self.tkClub, values=[club[0] for club in clubs])
        self.clubDropDown.grid(row=1, column=1, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Teams;''')
        teams = self.cursor.fetchall()

        self.teamDropDown = ttk.Combobox(self.root, textvariable=self.tkTeam, values=[team[0] for team in teams])
        self.teamDropDown.grid(row=2, column=1, columnspan=2, pady=2)

        self.fNameLabel = tk.Label(self.root, text='First Name:', justify='right')
        self.fNameLabel.grid(row=4, column=0, pady=2)
        self.fNameEntry = tk.Entry(self.root, textvariable=self.tkFName)
        self.fNameEntry.grid(row=4, column=1, pady=2)

        self.lNameLabel = tk.Label(self.root, text='Last Name:', justify='right')
        self.lNameLabel.grid(row=5, column=0, pady=2)
        self.lNameEntry = tk.Entry(self.root, textvariable=self.tkLName)
        self.lNameEntry.grid(row=5, column=1, pady=2)

        self.dobLabel = tk.Label(self.root, text='Date Of Birth:', justify='right')
        self.dobLabel.grid(row=6, column=0, pady=2)
        self.dobEntry = DateEntry(self.root, textvariable=self.tkDob, date_pattern='dd-mm-yyyy')
        self.dobEntry.grid(row=6, column=1, pady=2)

        self.hockeyWindowButton = tk.Button(self.root, text='Look-Up', command=self.submitLookup)  # Submits lookup
        self.hockeyWindowButton.grid(row=9, column=1, pady=2)

        self.signUpButton = tk.Button(self.root, text='Sign Up', command=self.showSignUpFields)  # Goes back to sign up
        self.signUpButton.grid(row=9, column=2, pady=2)

        self.loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)  # Goes back to login
        self.loginButton.grid(row=9, column=3, pady=2)

    def showMatchFields(self):
        self.clearLoginWindow()  # Clears window

        self.matchLabel = tk.Label(self.root, text='Match details', justify='center')
        self.matchLabel.grid(row=0, column=0, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Clubs;''')  # The following creates drop downs with existing clubs from the database
        clubs = self.cursor.fetchall()

        self.club1DropDown = ttk.Combobox(self.root, textvariable=self.tkClub1, values=[club[0] for club in clubs])
        self.club1DropDown.grid(row=1, column=0, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Teams;''')
        teams = self.cursor.fetchall()

        self.team1DropDown = ttk.Combobox(self.root, textvariable=self.tkTeam1, values=[team[0] for team in teams])
        self.team1DropDown.grid(row=2, column=0, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Clubs;''')
        clubs = self.cursor.fetchall()

        self.club2DropDown = ttk.Combobox(self.root, textvariable=self.tkClub2, values=[club[0] for club in clubs])
        self.club2DropDown.grid(row=1, column=2, columnspan=2, pady=2)

        self.cursor.execute('''SELECT name FROM Teams;''')
        teams = self.cursor.fetchall()

        self.team2DropDown = ttk.Combobox(self.root, textvariable=self.tkTeam2, values=[team[0] for team in teams])
        self.team2DropDown.grid(row=2, column=2, columnspan=2, pady=2)

        self.fNameLabel = tk.Label(self.root, text='Umpire First Name:', justify='right')
        self.fNameLabel.grid(row=4, column=0, pady=2)
        self.fNameEntry = tk.Entry(self.root, textvariable=self.tkFName)
        self.fNameEntry.grid(row=4, column=1, pady=2)

        self.lNameLabel = tk.Label(self.root, text='Umpire Last Name:', justify='right')
        self.lNameLabel.grid(row=5, column=0, pady=2)
        self.lNameEntry = tk.Entry(self.root, textvariable=self.tkLName)
        self.lNameEntry.grid(row=5, column=1, pady=2)

        self.hockeyWindowButton = tk.Button(self.root, text='Continue', command=self.openHockeyWindow)  # Progresses to the VAR window
        self.hockeyWindowButton.grid(row=9, column=1, pady=2)

        self.loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)  # Goes back to login
        self.loginButton.grid(row=9, column=2, pady=2)

    def submitSignUp(self):
        if self.tkEmail.get() != '' and self.tkFName.get() != '' and self.tkLName.get() != '' and self.tkPassword.get() != '' and self.tkClub.get() != '' and self.tkClub.get() != 'Select/Enter Your Club' and self.tkTeam.get() != 'Select/Enter Your Team':  # If each field has contents
            self.clearLoginWindow()
            if self.tkIsUmpire.get():
                self.userLoggedIn = True  # User is logged in and therefore can make challenges for others
                self.showLookupFields(text='Challenge Initiator:')
            else:
                self.showMatchFields()  # Straight to match fields as they are logging a match for themselves

            self.cursor.execute('''INSERT OR IGNORE INTO Clubs (name) VALUES (?);''', (self.tkClub.get(),))  # Add new club if it doesn't exist
            self.cursor.execute('''SELECT ID FROM Clubs WHERE name = ?;''', (self.tkClub.get(),))
            club = self.cursor.fetchone()[0]
            self.cursor.execute('''SELECT * FROM Teams WHERE club_id = ? AND name = ?;''', (club, self.tkTeam.get()))
            if self.cursor.fetchall() == []:
                self.cursor.execute(
                    '''INSERT OR IGNORE INTO Teams (club_id, name) VALUES (?, ?);''',
                    (club, self.tkTeam.get()))  # Add new team if it doesn't exist
            self.cursor.execute('''SELECT ID FROM Teams WHERE club_id = ? AND name = ?;''', (club, self.tkTeam.get()))
            team = self.cursor.fetchone()[0]
            self.cursor.execute(
                '''INSERT OR IGNORE INTO People (email, first_name, last_name, date_of_birth, team, is_umpire, password, challenges, successful_challenges) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);''',
                (self.tkEmail.get(), self.tkFName.get(), self.tkLName.get(), self.tkDob.get(), team, self.tkIsUmpire.get(),
                 self.tkPassword.get(), 0, 0))  # Add person
            self.cursor.execute('''SELECT ID FROM People WHERE email = ?;''', (self.tkEmail.get(),))
            ID = self.cursor.fetchone()[0]
            self.ID, self.clubID, self.teamID, self.email, self.fName, self.lName, self.dob, self.isUmpire, self.password = ID, club, team, self.tkEmail.get(), self.tkFName.get(), self.tkLName.get(), self.tkDob.get(), self.tkIsUmpire.get(), self.tkPassword.get()
        else:
            self.badDetails = tk.Label(self.root,
                                       text='Your details are not formatted correctly.\nMake sure each field has a value\nand your team is selected from the drop down.',
                                       fg='red')  # Display when fields not entered fully
            self.badDetails.grid(row=10, column=0, columnspan=2, pady=2)

    def submitLogin(self):
        self.cursor.execute('''SELECT * FROM People WHERE email = ? AND password = ?;''', (self.tkEmail.get(), self.tkPassword.get()))
        results = self.cursor.fetchall()
        if results != []:  # If Person exists
            self.clearLoginWindow()
            self.ID, self.email, self.fName, self.lName, self.dob, self.teamID, self.isUmpire, self.password, self.challenges, self.successfulChallenges = results[0]
            self.cursor.execute('''SELECT club_id FROM teams WHERE ID = ?;''', (self.teamID,))
            self.club = self.cursor.fetchone()[0]
            if results[0][6]:
                self.userLoggedIn = True
                self.showLookupFields(text='Challenge Initiator:')  # Move to select challenger if umpire
            else:
                self.showMatchFields()  # If not umpire, self as challenger
        else:
            self.badDetails = tk.Label(self.root, text='The details you have provided do not match an account.', fg='red')
            self.badDetails.grid(row=4, column=0, columnspan=2, pady=2)

    def submitLookup(self):
        self.cursor.execute('''SELECT * FROM Clubs WHERE name = ?;''', (self.tkClub.get(),))
        club = self.cursor.fetchone()[0]
        self.cursor.execute('''SELECT * FROM Teams WHERE name = ? AND club_id = ?;''', (self.tkTeam.get(), club))
        team = self.cursor.fetchone()[0]
        self.cursor.execute('''SELECT * FROM People WHERE team = ? AND first_name = ? AND last_name = ? AND date_of_birth = ?;''',
                            (team, self.tkFName.get(), self.tkLName.get(), self.tkDob.get()))
        self.challenger = self.cursor.fetchone()
        if self.challenger != []:
            self.clearLoginWindow()
            if not self.userLoggedIn:
                self.displayLookup()  # Lookup rather than challenger
            else:
                self.showMatchFields()  # Challenger
        else:
            self.badDetails = tk.Label(self.root, text='The details you have provided do not match an account.',
                                       fg='red')
            self.badDetails.grid(row=4, column=0, columnspan=2, pady=2)

    def onClubChange(self, *args):  # Used to display all teams and clubs that might be associated to the current input
        self.cursor.execute('''SELECT * FROM Clubs WHERE name LIKE ?''', (self.tkClub.get() + '%',))
        clubs = self.cursor.fetchall()
        teams = []
        if clubs != []:
            placeholders = ', '.join('?' for club in clubs)
            self.cursor.execute(f'''SELECT name FROM Teams WHERE club_id IN ({placeholders});''',
                                [club[0] for club in clubs])
            teams = self.cursor.fetchall()
        self.clubDropDown['values'] = [club[1] for club in clubs]
        self.teamDropDown['values'] = [team[0] for team in teams]

    def onClub1Change(self, *args):  # Used to display all teams and clubs that might be associated to the current input
        self.cursor.execute('''SELECT * FROM Clubs WHERE name LIKE ?''', (self.tkClub1.get() + '%',))
        clubs = self.cursor.fetchall()
        teams = []
        if clubs != []:
            placeholders = ', '.join('?' for club in clubs)
            self.cursor.execute(f'''SELECT name FROM Teams WHERE club_id IN ({placeholders});''',
                                [club[0] for club in clubs])
            teams = self.cursor.fetchall()
        self.club1DropDown['values'] = [club[1] for club in clubs]
        self.team1DropDown['values'] = [team[0] for team in teams]

    def onClub2Change(self, *args):  # Used to display all teams and clubs that might be associated to the current input
        self.cursor.execute('''SELECT * FROM Clubs WHERE name LIKE ?''', (self.tkClub2.get() + '%',))
        clubs = self.cursor.fetchall()
        teams = []
        if clubs != []:
            placeholders = ', '.join('?' for club in clubs)
            self.cursor.execute(f'''SELECT name FROM Teams WHERE club_id IN ({placeholders});''',
                                [club[0] for club in clubs])
            teams = self.cursor.fetchall()
        self.club2DropDown['values'] = [club[1] for club in clubs]
        self.team2DropDown['values'] = [team[0] for team in teams]

    def displayLookup(self):
        self.cursor.execute('''SELECT SUM(challenges), SUM(successful_challenges) FROM People WHERE team = ?;''', (self.challenger[5],))  # Gets the team challenges
        teamChallenges, teamSuccessfulChallenges = self.cursor.fetchone()
        self.cursor.execute('''SELECT COUNT(*) FROM Matches WHERE home_team = ? OR away_team = ?;''', (self.challenger[5], self.challenger[5]))  # Gets all matches for their team
        teamMatchesPlayed = self.cursor.fetchone()

        teamTitleLabel = tk.Label(self.root, text='Team Stats:')
        teamTitleLabel.grid(row=2, column=0, pady=2)
        teamGamesPlayesLabel = tk.Label(self.root, text=f'Games played: {teamMatchesPlayed}')
        teamGamesPlayesLabel.grid(row=3, column=0, pady=2)
        teamChallengeFractionLabel = tk.Label(self.root,
                                              text=f'(Successful Challenges)/(Total Challenges)  -  {teamSuccessfulChallenges}/{teamChallenges}  -  {round((teamSuccessfulChallenges / teamChallenges) * 100, 2)}%')
        teamChallengeFractionLabel.grid(row=4, column=0, pady=2)

        playerTitleLabel = tk.Label(self.root, text='Player Stats:')
        playerTitleLabel.grid(row=5, column=0, pady=2)
        playerChallengeFractionLabel = tk.Label(self.root,
                                              text=f'(Successful Challenges)/(Total Challenges)  -  {self.challenger[9]}/{self.challenger[8]}  -  {round((self.challenger[9] / self.challenger[8]) * 100, 2)}%')
        playerChallengeFractionLabel.grid(row=6, column=0, pady=2)

        loginButton = tk.Button(self.root, text='Log In', command=self.showLoginFields)
        loginButton.grid(row=7, column=0, pady=2, padx=2)
        signUpButton = tk.Button(self.root, text='Sign Up', command=self.showSignUpFields)
        signUpButton.grid(row=7, column=1, pady=2, padx=2)

    def openHockeyWindow(self):
        matchData = ((self.tkClub1.get(), self.tkTeam1.get()), (self.tkClub2.get(), self.tkTeam2.get()))

        self.cursor.execute('''SELECT * FROM Clubs WHERE name = ?;''', (matchData[0][0],))
        club1ID = self.cursor.fetchone()[0]
        self.cursor.execute('''SELECT * FROM Teams WHERE club_id = ? AND name = ?;''', (club1ID, matchData[0][1]))
        team1ID = self.cursor.fetchone()[0]
        self.cursor.execute('''SELECT * FROM Clubs WHERE name = ?;''', (matchData[1][0],))
        club2ID = self.cursor.fetchone()[0]
        self.cursor.execute('''SELECT * FROM Teams WHERE club_id = ? AND name = ?;''', (club2ID, matchData[1][1]))
        team2ID = self.cursor.fetchone()[0]
        self.cursor.execute('''INSERT OR IGNORE INTO Matches (home_team, away_team, umpire, date) VALUES (?, ?, ?, ?);''',
                            (team1ID, team2ID, self.ID, datetime.datetime.today().strftime('%d-%m-%Y')))
        self.cursor.execute('''SELECT ID FROM Matches WHERE home_team = ? AND away_team = ? AND umpire = ? AND date = ?;''', (team1ID, team2ID, self.ID, datetime.datetime.today().strftime('%d-%m-%Y')))
        matchID = self.cursor.fetchone()[0]  # Find clubs/teams in match

        if self.isUmpire:
            user = peopleClasses.Umpire(self.challenger[0], matchData[0], matchData[1], umpireId=self.ID)
        else:
            if self.teamID == team1ID:
                isHome = True
            else:
                isHome = False
            user = peopleClasses.Player(self.ID, matchData[0], matchData[1], isHome=isHome)
        self.clearLoginWindow()
        self.conn.commit()
        self.conn.close()  # Commit database to be opened later in different thread
        hockeyTkinterWindow(matchID, user, root=self.root)  # Initialise the hockeyVAR window

    def clearLoginWindow(self):
        for widget in self.root.winfo_children():  # Loops through tkinter widgets and destroys them
            widget.destroy()


class hockeyTkinterWindow:
    def __init__(self, matchID, user, root=None):
        self.frameControlFlag = 0  # -1 for rewinding, 1 for forwarding, 0 for all else
        self.video = None  # Initialise video, will later be assigned as an instance of custom HockeyVideo object
        self.matchID = matchID  # matchID in database
        self.clipID = None  # Initialise clipID
        self.user = user  # Set user
        if root != None:  # If a root was passed, create with that root
            self.createWindow(root=root)
        else:
            self.createWindow()

    def createWindow(self, root=None):
        if root == None:  # Create a window if no root was passed
            self.root = tk.Tk()
            self.root.minsize(250, 300)
        else:
            self.root = root

        self.mouseX = 0
        self.mouseY = 0

        self.submitVideoButton = tk.Button(self.root, text='Submit File', command=self.submitVideo,
                                           activebackground='blue', activeforeground='white')
        self.submitVideoButton.grid(row=0, column=0, pady=2)  # Submit a video

        self.root.after(500, self.frameControlLoop)  # Wait 500ms before running frameControlLoop

    def createButtonsWidget(self):  # Creates buttons with images for the UI
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
        if self.frameControlFlag != 0:  # If rewinding or forwarding
            if self.frameControlFlag == 1 and self.video.frameNum + self.video.frameJump <= self.video.lastFrame:
                self.video.frameNum += self.video.frameJump  # Forward

            if self.frameControlFlag == -1 and self.video.frameNum - self.video.frameJump >= 0:
                self.video.frameNum -= self.video.frameJump  # Rewind

            self.video.nextFrameDisplayTime = time.time()

        if hasattr(self, 'video'):  # If a video has been created
            if hasattr(self.video, 'challengeCorrect'):
                if self.video.challengeCorrect != None:  # If a VAR has been initiated and completed
                    conn = sqlite3.connect('hockey_video.db')
                    cursor = conn.cursor()
                    cursor.execute('''INSERT OR IGNORE INTO Challenges (frame_num, challenger, challenge_correct, clip_id) VALUES (?, ?, ?, ?);''', (self.video.frameNum, self.user.userID, self.video.challengeCorrect, self.clipID))  # Create a challenge in the database
                    successfulBool = 0
                    if self.video.challengeCorrect:
                        successfulBool = 1
                    cursor.execute('''UPDATE People SET challenges = challenges + 1 WHERE ID = ?;''', (self.user.userID,))  # Update user with challenge
                    cursor.execute(
                        '''UPDATE People SET successful_challenges = successful_challenges + ? WHERE ID = ?;''',
                        (successfulBool, self.user.userID))
                    self.video.challengeCorrect = None
                    conn.commit()
                    conn.close()

        try:
            self.root.after(self.video.frameJump * 200, self.frameControlLoop)  # Recall this function in 200ms * the jump in frames to pace the forwarding/rewinding
        except:
            self.root.after(200, self.frameControlLoop)  # Recall after 200ms if frameJump does not exist

    def submitVideo(self):
        try:
            self.video.videoEnded = True  # Try to end any existing video
        except:
            print('no video')
        submitVideoThread = threading.Thread(target=self.processVideo)  # Start thread for processing the video independent of the window
        submitVideoThread.start()

    def processVideo(self):
        conn = sqlite3.connect('hockey_video.db')
        cursor = conn.cursor()
        frameJump = 1  # Set jump in frames for performance
        filename = fd.askopenfilename()
        cursor.execute('''INSERT OR IGNORE INTO Clips (path, match_id) VALUES (?, ?)''', (filename, self.matchID))  # Create clip in db
        cursor.execute('''SELECT ID FROM Clips WHERE path = ? AND match_id = ?;''', (filename, self.matchID))
        self.clipID = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        self.video = videoClass.HockeyVideo(self.root, filename, frameJump=frameJump, debug=True)  # Create hockey video
        displayThread = threading.Thread(target=self.video.displayFrames)  # Start the thread to display the video independent of window
        displayThread.start()
        self.createButtonsWidget()  # Create the widget which contains the UI for media control

    def normalSpeed(self):  # Video speed control
        self.video.speed = 1
        self.video.nextFrameDisplayTime = time.time()

    def halfSpeed(self):  # Halves the video speed
        self.video.speed = 0.5
        self.video.nextFrameDisplayTime = time.time()

    def pauseVideo(self):  # Sets paused flag
        self.video.isPaused = True

    def playVideo(self):  # Sets paused flag and resets when the next image should be displayed
        self.video.isPaused = False
        self.video.nextFrameDisplayTime = time.time()

    def reverseFrame(self, event):  # Sets frameControlFlag for the frameControlLoop function
        self.pauseVideo()
        self.frameControlFlag = -1
        if self.video.frameNum - self.video.frameJump >= 0:
            self.video.frameNum -= self.video.frameJump

    def forwardFrame(self, event):  # Sets frameControlFlag for the frameControlLoop function
        self.pauseVideo()
        self.frameControlFlag = 1
        if self.video.frameNum + self.video.frameJump <= self.video.lastFrame:
            self.video.frameNum += self.video.frameJump

    def stopFrameControl(self, event):  # Stops rewind/forwarding
        self.frameControlFlag = 0

    def challenge(self):  # Starts VAR
        self.video.footIdentified = True
        self.video.isPaused = False
