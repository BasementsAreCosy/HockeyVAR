import windowClasses
import sqlite3

conn = sqlite3.connect('hockey_video.db')  # Create or connect to a database
cursor = conn.cursor()

### The following creates any missing tables in the database

cursor.execute('''
            CREATE TABLE IF NOT EXISTS Matches
            (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                home_team INTEGER NOT NULL REFERENCES Teams(ID),
                away_team INTEGER NOT NULL REFERENCES Teams(ID),
                umpire INTEGER REFERENCES People(ID),
                date DATE
            );''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS Teams
            (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                club_id INTEGER NOT NULL REFERENCES Clubs(ID),
                name TEXT NOT NULL
            );''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clubs
            (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS People
            (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT,
                date_of_birth DATE,
                team INTEGER REFERENCES Teams(ID),
                is_umpire BOOLEAN,
                password TEXT NOT NULL,
                challenges INTEGER,
                successful_challenges INTEGER
            );''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS Clips
            (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                match_id INTEGER REFERENCES Matches(ID)
            );''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS Challenges
            (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                frame_num INTEGER,
                challenger INTEGER REFERENCES People(ID),
                challenge_correct BOOLEAN,
                clip_id INTEGER REFERENCES Clips(ID)
            );''')

conn.commit()
conn.close()  # Must commit and close before opening the window as sqlite does not function across several threads

window = windowClasses.menuWindow()  # Initialises the Tkinter window
