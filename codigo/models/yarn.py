"""
autor: Valentina Garrido
"""

import numpy as np
from models.block import Block
import scene_graph_3D as sg
import transformations as tr
import easy_shaders as es
from OpenGL.GL import GL_REPEAT, GL_NEAREST

from models.movingQuad import MCListener
from models.touchBlock import TouchBlock
from textureSphere import generateSemiSphereTextureNormals

from models.staticViewObjects import WinCG


class Yarn(TouchBlock, MCListener):
    def __init__(self, size, name="Yarn", bg=None):
        super().__init__(size, size, size, name)
        self.enable_game_over = False
        self.t = 0.0

        self.bg = None
        self.world_model = None
        self.game_over_cg = None
        self.update_list = None

    def set_model_texture(self, texture_filename: str = None):
        if texture_filename:
            sphere = generateSemiSphereTextureNormals('textures/rainbow_yarn.png', 20, 20)
            gpu_sphere = es.toGPUShape(sphere, GL_REPEAT, GL_NEAREST)
            self.set_model(gpu_sphere)

    def notify(self):
        for obs in self._observers:
            obs.on_yarn_touch(self)

    def set_bg(self, bg):
        self.bg = bg

    def set_world_model(self, world_model):
        self.world_model = world_model

    def set_update_list(self, update_list):
        self.update_list = update_list

    def update_winning_status(self, mc):
        if self.in_boundary(mc) and self.enable_game_over:
            if not mc.game_over:
                self.on_win()
            mc.game_over = True
            mc.won = True

    def on_win(self):
        self.bg.set_game_over_background()
        self.game_over_cg = WinCG()
        self.world_model.children += [self.game_over_cg.model]
        self.update_list += [self.game_over_cg]


    def update_time(self, dt):
        self.t += dt

    def grow_and_shrink(self,dt):
        self.update_time(dt)
        yarn = sg.findNode(self.model, self.name)
        resize = self.width*(1+0.05*np.sin(5*self.t))
        yarn.transform = tr.scale(resize,resize,resize)
