import windowClass
import sqlite3

conn = sqlite3.connect('hockey_video.db')
cursor = conn.cursor()

cursor.execute('''
            CREATE TABLE IF NOT EXISTS Matches
            (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                home_team INTEGER NOT NULL REFERENCES Teams(ID),
                away_team INTEGER NOT NULL REFERENCES Teams(ID),
                umpire INTEGER REFERENCES People(ID)
            );''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS Teams
            (
                ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                club_id INTEGER NOT NULL REFERENCES Clubs(ID),
                name TEXT NOT NULL,
                challenges INTEGER,
                successful_challenges INTEGER
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
                password TEXT NOT NULL
            );''')
# Not covering User Auth and Encryption for NEA course. In practice and production, User Auth would be developed using appropriate libraries

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
                challenge_correct BOOLEAN
                clip_id INTEGER REFERENCES Clips(ID)
            );''')

#cursor.execute('''INSERT INTO Clubs (name) VALUES (?)''', ('HailshamHC',))
#cursor.execute('''INSERT INTO people (first_name, last_name, date_of_birth, team, is_umpire, password) VALUES (?, ?, ?, ?, ?, ?);''', ('Fin', 'Jones', '05/09/2006', 1, False, '1234'))


cursor.execute('''SELECT * FROM Clubs;''')
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.execute('''SELECT * FROM Teams;''')
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.execute('''SELECT * FROM People;''')
rows = cursor.fetchall()
for row in rows:
    print(row)

window = windowClass.menuWindow(conn, cursor)

conn.commit()

'''
PLAN:

Create People class (inheritance):
    - Player:
        ~ Polymorphism: challenges affects self
    - Umpire:
        ~ Polymorphism: challenges affects player/umpire selected in log in




'''