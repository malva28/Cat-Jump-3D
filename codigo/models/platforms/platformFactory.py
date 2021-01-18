"""
autor: Valentina Garrido
"""

from models.platforms.platform import Platform, FakePlatform


class PlatformFactory:
    def __init__(self, width: float, depth: float, height: float, world=None, timer: float = 3., gravity: float = 1/20, quadName: str = "Platform"):
        self.width = width
        self.depth = depth
        self.height = height
        self.name = quadName
        self.timer = timer
        self.gravity = gravity
        self.world = world
        self.pos = [0., 0., 0.]
        self.texture_filename = None

    def set_positions(self, x: float, y: float, z: float):
        self.pos = [x, y, z]

    def set_texture(self, texture_filename):
        self.texture_filename = texture_filename

    def apply_settings(self, plat):
        plat.set_model_texture(self.texture_filename)
        plat.set_init_pos(*self.pos)

    def make_platform(self):
        new_plat = Platform(self.width, self.depth, self.height, self.name)
        self.apply_settings(new_plat)
        return new_plat

    def make_fake_platform(self):
        new_fake = FakePlatform(self.width, self.depth, self.height, self.world,self.timer, self.gravity, self.name)
        self.apply_settings(new_fake)
        return new_fake
