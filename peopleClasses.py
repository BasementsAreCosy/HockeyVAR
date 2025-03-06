class Person:
    def __init__(self, home, away):
        self.home = home
        self.away = away

    def recordChallenge(self):
        pass

    def getSubjectData(self):
        pass

class Umpire(Person):
    def __init__(self, home, away, isHome=None):
        super().__init__(home, away)

    def recordChallenge(self):
        pass

    def getSubjectData(self):
        pass

class Player(Person):
    def __init__(self, home, away, isHome):
        super().__init__(home, away)
        self.isHome = isHome

    def getTeam(self):
        if self.isHome:
            return self.home
        return self.away

    def getOpposition(self):
        if self.isHome:
            return self.away
        return self.home
