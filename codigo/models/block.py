"""
autor: Valentina Garrido
"""

from models.quad import Quad
import scene_graph_3D as sg
import transformations as tr
import easy_shaders as es
import basic_shapes as bs
from OpenGL.GL import *


from typing import Optional

class Block:
    def __init__(self, width: float, depth: float, height: float, quadName: str = "Quad"):
        self.width = width
        self.height = height
        self.depth = depth

        self.drawing = True

        self.name = quadName
        self.model = None

        self.delta = 0.001

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0


    def copy(self):
        newBlock = Block(self.width, self.height, self.depth, self.name)
        newBlock.model = sg.copyNode(self.model)
        newBlock.delta = self.delta
        newBlock.pos_x = self.pos_x
        newBlock.pos_y = self.pos_y
        newBlock.pos_z = self.pos_z
        return newBlock

    def set_model(self, gpu_quad):
        quad = sg.SceneGraphNode(self.name)

        quad.transform = tr.scale(self.width, self.depth, self.height)
        quad.children += [gpu_quad]

        self.model = sg.SceneGraphNode(self.name + "Tr")
        self.model.children += [quad]

    def set_model_color(self, color):
        gpu_quad = es.toGPUShape(bs.createColorQuad(*color))
        self.set_model(gpu_quad)

    def set_model_texture(self, texture_filename: str = None):
        if texture_filename:
            gpu_quad = es.toGPUShape(bs.createTextureNormalsCube(texture_filename), GL_REPEAT, GL_NEAREST)
            self.set_model(gpu_quad)

    def set_init_pos(self, ini_x, ini_y, ini_z):
        # ini_pos = sg.findNode(self.model, self.name + "Tr")
        self.pos_x = ini_x
        self.pos_y = ini_y
        self.pos_z = ini_z

    def move_position(self, dx, dy, dz):
        self.pos_x += dx
        self.pos_y += dy
        self.pos_z += dz

    def translate(self, node, dx, dy, dz):
        self.move_position(dx,dy,dz)
        sg.translate(node, dx, dy, dz)

    def update_translate_matrix(self):
        self.model.transform = tr.translate(self.pos_x, self.pos_y, self.pos_z)

    def draw(self, projection, view, pipeline):
        sg.drawSceneGraphNode(self.model, projection,  view, pipeline=pipeline)

    def rightLim(self):
        return self.pos_x + self.width * 0.5

    def leftLim(self):
        return self.pos_x - self.width * 0.5

    def frontLim(self):
        return self.pos_y + self.depth * 0.5

    def backLim(self):
        return self.pos_y - self.depth * 0.5

    def upperLim(self):
        try:
            return self.pos_z + self.height * 0.5
        except TypeError:
            print("pos_z: ", self.pos_z)
            print("height: ", self.height)
            raise TypeError

    def lowerLim(self):
        return self.pos_z - self.height * 0.5

    def disable_drawing(self):
        self.drawing = False
        if self.model:
            self.model.drawing = False

    def enable_drawing(self):
        self.drawing = True
        if self.model:
            self.model.drawing = True

    def __str__(self):
        r = 2
        msg = 'Block: {6}\nXYZ pos: ({0},{1},{2})\nDimensions: (w: {3}, d: {4}, h:{5})'
        return msg.format(round(self.pos_x, r), round(self.pos_y, r),round(self.pos_y, r),
                          round(self.width, r), round(self.depth, r),round(self.height, r),
                          self.name)
