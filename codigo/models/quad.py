"""
autor: Valentina Garrido
"""

import transformations as tr
import basic_shapes as bs
import scene_graph_3D as sg
import easy_shaders as es


class Quad(sg.SceneGraphNode):
    def __init__(self, name, color, w=1., h=1.):
        # name is str name to identify quad
        # w is square weight and h is square height
        # color is a rgb triplet for quad color
        # if w=1 and h=1, the resulting square is centered at (0,0)
        # and the upper left point and bottom right points are (-0.5,0.5) and (0.5,-0.5) respectively

        self.w = w
        self.h = h
        sx = w
        sy = h

        super().__init__(name)

        gpu_quad = es.toGPUShape(bs.createColorQuad(*color))
        self.transform = tr.scale(sx, sy, 1)
        self.children += [gpu_quad]