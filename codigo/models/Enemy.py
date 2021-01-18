"""
autor: Valentina Garrido
"""

from models.block import Block
import numpy as np
import basic_shapes as bs
import easy_shaders as es
from OpenGL.GL import GL_REPEAT, GL_NEAREST

import scene_graph_3D as sg

from models.touchBlock import TouchBlock


class Enemy(TouchBlock):
    def __init__(self, width: float, depth: float, height: float,
                 platform_sep, platform_len, parent_generator=None,
                 quad_name: str = "Enemy"):
        super().__init__(width, depth, height, quad_name)
        self.parent_generator = parent_generator
        self.platform_sep = platform_sep
        self.platform_len = platform_len
        self.spawn_radius = 2.
        self.spawn_angle = 0.
        self.disable_drawing()

    def set_model_texture(self, texture_filename: str = None):
        if texture_filename:
            cube = bs.createTextureTransparentNormalsCube(texture_filename)
            gpu_cube = es.toGPUShape(cube, GL_REPEAT, GL_NEAREST)
            self.set_model(gpu_cube)

            enemy = sg.findNode(self.model, self.name)
            sg.rotationZ(enemy, np.pi/2)


    def activate(self):
        self.enable_drawing()
        self.reset_movement()

    def possible_z_positions(self):
        return [(i-0.9)*self.platform_sep for i in range(self.platform_len)]

    def possible_xy_centers(self):
        return [[-0.7,-0.35], [-0.35,0.35], [0.0,-0.35], [0.35, 0.35], [0.7,-0.35]]

    def reset_movement(self):
        old_x = self.pos_x
        old_y = self.pos_y
        old_z = self.pos_z
        old_spawn_angle = self.spawn_angle

        enemy = sg.findNode(self.model, self.name)
        sg.rotationZ(enemy, -old_spawn_angle)

        self.spawn_angle = np.random.random()*np.pi*2

        sg.rotationZ(enemy, self.spawn_angle)

        #self.spawn_angle = -np.pi
        self.vel = 0.4

        self.z = np.random.choice(self.possible_z_positions())

        i_center = np.random.choice(range(len(self.possible_xy_centers())))
        center = self.possible_xy_centers()[i_center]

        # DESCOMENTAR ESTE CÓDIGO PARA QUE LAS POLILLAS APAREZCAN SÓLO EN EL PRIMER NIVEL
        #self.z = -0.72

        self.dir_x = self.spawn_radius * np.cos(self.spawn_angle)
        self.sign_x = 1 if self.dir_x >= 0 else -1
        self.dir_y = self.spawn_radius * np.sin(self.spawn_angle)
        self.sign_y = 1 if self.dir_y >= 0 else -1

        self.translate(self.model,-old_x, -old_y, -old_z)
        self.translate(self.model,-self.dir_x+ center[0], -self.dir_y+ center[1], self.z)


    def fly(self, dt):
        if self.drawing:
            dx = self.dir_x*dt*self.vel
            dy = self.dir_y*dt*self.vel
            self.translate(self.model, dx,dy,0)

            if self.pos_x*self.sign_x > self.sign_x*self.dir_x \
                    and self.sign_y*self.pos_y > self.sign_y*self.dir_y:
                self.disable_drawing()
                if self.parent_generator:
                    self.parent_generator.delete(self)


    def notify(self):
        for obs in self._observers:
            obs.on_enemy_touch(self)


class EnemyFactory:
    def __init__(self, width: float, depth: float, height: float,
                 min_z, max_z, parent_generator = None, world = None, mc = None, quadName: str = "Enemy"):
        self.width = width
        self.depth = depth
        self.height = height
        self.min_z = min_z
        self.max_z = max_z
        self.parent_generator = parent_generator
        self.name = quadName
        self.world = world
        self.mc = mc

    def set_texture(self, texture_filename):
        self.texture_filename = texture_filename

    def add_observers(self, world, mc):
        self.world = world
        self.mc = mc

    def apply_settings(self, enemy):
        enemy.set_model_texture(self.texture_filename)
        enemy.add_observer(self.world)
        enemy.add_observer(self.mc)

    def make_enemy(self):
        new_enemy = Enemy(self.width, self.depth, self.height, self.min_z, self.max_z, self.parent_generator, self.name)
        self.apply_settings(new_enemy)
        return new_enemy


class EnemyGenerator:
    def __init__(self, min_z, max_z):
        self.enemies = []
        self.inactive = []
        self.generate = True
        self.max_n_enemies = 8
        self.appear_tolerance = 0.02
        self.enemy_factory = EnemyFactory(0.15, 0.1, 0.1, min_z, max_z, parent_generator=self)

    def init_enemies(self):
        for i in range(self.max_n_enemies):
            self.inactive.append(self.enemy_factory.make_enemy())

    def set_texture(self, texture_filename):
        self.enemy_factory.set_texture(texture_filename)

    def set_observers(self, world, mc):
        self.enemy_factory.add_observers(world, mc)


    def create_enemy(self):
        if len(self.enemies) >= self.max_n_enemies or not self.generate:
            return
        if np.random.random() < self.appear_tolerance:
            # print("number of enemies: ", len(self.enemies))
            new_enemy = self.inactive.pop()
            new_enemy.activate()
            self.enemies.append(new_enemy)

    def update(self, dt):
        if self.generate:
            for enemy in self.enemies:
                enemy.fly(dt)

    def get_active_enemies(self):
        return self.enemies

    def delete(self, enemy: Enemy):
        self.enemies.remove(enemy)
        self.inactive.append(enemy)

    def draw(self, pipeline, projection, view ):
        for enemy in self.enemies:
            enemy.draw(projection, view, pipeline)
