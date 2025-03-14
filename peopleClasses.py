class Person:
    def __init__(self, userID, home, away):
        self.userID = userID
        self.home = home
        self.away = away

    def recordChallenge(self):
        pass

    def getSubjectData(self):
        pass

class Umpire(Person):
    def __init__(self, challengerID, home, away, umpireId=None, isHome=None):
        self.umpireID = umpireId
        super().__init__(challengerID, home, away)

    def recordChallenge(self):
        pass

    def getSubjectData(self):
        pass

class Player(Person):
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
