"""
autor: Valentina Garrido
"""

from models.block import Block
import scene_graph_3D as sg

from withinEps import *


class _AbstractPlatform(Block):
    def __init__(self, width: float, depth: float, height: float, quadName: str):
        super().__init__(width, depth, height,   quadName)
        self.stepped_on = False
        self.delta = 0.02

        self._observers = []

    def add_observer(self, obs):
        if obs not in self._observers:
            self._observers.append(obs)

    def notify(self):
        for obs in self._observers:
            obs.on_platform_collision(self)

    def upperCollide(self, cat):
        # print('cat lower lim: {}\nplatform upper lim: {}'.format(cat.lowerLim(), self.upperLim()))
        if within_eps(cat.lowerLim(), self.upperLim(), self.delta):
            if cat.rightLim() >= self.leftLim() and cat.leftLim() <= self.rightLim() \
                    and cat.frontLim() >= self.backLim() and cat.backLim() <= self.frontLim() and cat.jump_state() != 1:
                if not self.stepped_on:
                    self.notify()
                return True
        return False


class Platform(_AbstractPlatform):
    def __init__(self, width: float, depth: float, height: float, quadName: str = "Platform"):
        super().__init__(width, depth, height,   quadName)

    def copy(self):
        newPlat = Platform(self.width, self.depth, self.height, self.name)
        newPlat.model = sg.copyNode(self.model)
        newPlat.pos_x = self.pos_x
        newPlat.pos_y = self.pos_y
        newPlat.pos_z = self.pos_z
        return newPlat


class FakePlatform(_AbstractPlatform):
    def __init__(self, width: float, depth: float, height: float, world, timer: float = 3., gravity: float = 1/20, quadName: str = "FakePlatform"):
        super().__init__(width, depth, height,   quadName)
        self.timer = timer
        self.gravity = gravity
        self.vz = 0.
        self.prev_tremor = None
        self.add_observer(world)
        self.add_observer(self)

    def notify(self):
        for obs in self._observers:
            obs.on_fake_platform_collision(self)

    def set_model(self, gpu_quad):
        super().set_model(gpu_quad)
        self.add_tremor_node()

    def add_tremor_node(self):
        tremor = sg.SceneGraphNode(self.name + "Tremor")
        fake = sg.findNode(self.model, self.name)
        self.model.children = [tremor]
        tremor.children = [fake]

    def on_fake_platform_collision(self, listener):
        self.stepped_on = True
        dt = 0.01
        self.tremor(dt)

    def update(self, t, dt):
        self.tremor(dt)

    def tremor(self, dt):
        factor = self.width*0.1
        sign = [-1,1]
        tremor_vec = np.array([factor * np.random.choice(sign)* np.random.random() for i in range(3)])
        tremor = sg.findNode(self.model, self.name + "Tremor")

        if self.prev_tremor is not None:
            self.translate(tremor, *(-self.prev_tremor))
            self.prev_tremor = None
        else:
            self.translate(tremor, *tremor_vec)
            self.prev_tremor = tremor_vec
        self.timer -= dt
        self.fall(dt, self.gravity)

    def fall(self, dt, gravity):
        if self.timer < 0.:
            self.vz -= gravity
            self.translate(self.model, 0.,0., self.vz*dt)
