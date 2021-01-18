"""
autor: Valentina Garrido
"""

class Walls:
    def __init__(self, leftBound: float, rightBound: float, backBound: float, frontBound: float):
        self.leftBound = leftBound
        self.rightBound = rightBound
        self.backBound = backBound
        self.frontBound = frontBound
        self.delta = 0.001

    def leftCollide(self, cat) -> bool:
        if cat.leftLim() <= self.leftBound + self.delta:
            return True
        return False

    def rightCollide(self, cat) -> bool:
        if cat.rightLim() >= self.rightBound - self.delta:
            return True
        return False

    def backCollide(self, cat):
        if cat.backLim() <= self.backBound + self.delta:
            return True
        return False

    def frontCollide(self, cat):
        if cat.frontLim() >= self.frontBound - self.delta:
            return True
        return False
