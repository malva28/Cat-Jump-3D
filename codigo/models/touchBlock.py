"""
autor: Valentina Garrido
"""

from models.block import Block


class TouchBlock(Block):
    def __init__(self, width: float, depth: float, height: float, quadName: str = "Quad"):
        super().__init__(width, depth, height, quadName)
        self._observers = []

    def add_observer(self, obs):
        if obs not in self._observers:
            self._observers.append(obs)

    def notify(self):
        for obs in self._observers:
            obs.on_touch(self)

    def in_boundary(self, mc):
        if not mc.can_touch:
            return False
        if self.leftLim() < mc.pos_x and mc.pos_x < self.rightLim():
            if self.lowerLim() < mc.pos_z and mc.pos_z < self.upperLim():
                if self.backLim() < mc.pos_y and mc.pos_y < self.frontLim():
                    self.notify()
                    return True
        return False