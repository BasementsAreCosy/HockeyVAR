class Person:
    def __init__(self, userID, home, away):  # Class to store home/away and user for a specific match
        self.userID = userID
        self.home = home
        self.away = away

class Umpire(Person):  # Inherit from person, includes umpireID as well as the challenger
    def __init__(self, challengerID, home, away, umpireId=None, isHome=None):
        self.umpireID = umpireId
        super().__init__(challengerID, home, away)

class Player(Person):  # Has challenger as themself, no umpireID
    def __init__(self, userID, home, away, isHome):
        self.isHome = isHome
        super().__init__(userID, home, away)

    def getTeam(self):
        if self.isHome:
            return self.home
        return self.away

    def getOpposition(self):
        if self.isHome:
            return self.away
        return self.home
