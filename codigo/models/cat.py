"""
autor: Valentina Garrido
"""

from models.movingQuad import MovingQuad

import scene_graph_3D as sg
import transformations as tr
import easy_shaders as es
import basic_shapes as bs
import numpy as np
from OpenGL.GL import *

from sprites3D import create_3D_sprite_single_color


class Cat(MovingQuad):
    def __init__(self, width, depth, height):
        super().__init__(width, depth, height, "Cat")

        self.base_color = {'r': 0.1, 'g': 0.1, 'b':0.3 }
        self.moving_sprites = []
        self.jumping_sprites = []
        self.idle_sprite = []

        self.load_sprites()
        self.set_model(self.idle_sprite[0])

        self.current_idle_sprite = 0
        self.current_jump_sprite = 0
        self.current_mov_sprite = 0
        self.t = 0

        cat = sg.findNode(self.model, self.name)
        sg.rotationY(cat, np.pi/2)
        sg.scale(cat, -1, 1, 1)

    def set_sprite(self, gpu_sprite):
        cat = sg.findNode(self.model, self.name)
        cat.children = [gpu_sprite]

    def load_moving_sprites(self):
        filenames = []
        name_base = "textures/catRunning{}{}.png"
        for i in range(1, 13):
            u = i % 10
            d = i // 10
            filenames.append(name_base.format(str(d), str(u)))
        self.moving_sprites = [es.toGPUShape(create_3D_sprite_single_color(img, self.base_color)) for img in
                               filenames]

    def load_jumping_sprites(self):
        filenames = ["textures/catJumping01.png",
                     "textures/catRunning04.png",
                     "textures/catRunning05.png",
                     "textures/catRunning06.png",
                     "textures/catJumping02.png"]
        self.jumping_sprites = [es.toGPUShape(create_3D_sprite_single_color(img, self.base_color)) for img in
                               filenames]

    def load_sprites(self):
        self.load_moving_sprites()
        self.load_jumping_sprites()
        self.idle_sprite = [es.toGPUShape(create_3D_sprite_single_color("textures/catIdle.png", self.base_color), GL_REPEAT, GL_NEAREST)]

    def update_jump_sprite(self, dt):
        if self.jump_state() == 0:
            return
        if self.jump_state() == 2:
            self.t += dt
            if self.vz > self.maxVz/10:
                self.current_jump_sprite = 1
            elif self.vz < -self.maxVz/10:
                self.current_jump_sprite = 3
            else:
                self.current_jump_sprite = 2
        else:
            self.t = 0
            if self.jump_state() == 1:
                self.current_jump_sprite = 0
            elif self.jump_state() == 3:
                self.current_jump_sprite = 4

    def update_moving_sprite(self, dt):
        self.t += dt
        if np.fabs(self.vxy) > 0 and self.t > np.fabs(0.03/self.vxy):
            self.current_mov_sprite = (self.current_mov_sprite + 1) % 12
            self.t = 0

    def update_sprite(self, dt):
        if self.is_idle():
            self.set_sprite(self.idle_sprite[self.current_idle_sprite])
        else:
            if self.midair:
                self.update_jump_sprite(dt)
                self.set_sprite(self.jumping_sprites[self.current_jump_sprite])
            else:
                self.update_moving_sprite(dt)
                self.set_sprite(self.moving_sprites[self.current_mov_sprite])

    def update_positions(self, dt):
        self.update_sprite(dt)
        super().update_positions(dt)