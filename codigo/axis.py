"""
Hacemos los modelos del auxiliar
"""

import basic_shapes as bs
import transformations2 as tr
import easy_shaders as es
from OpenGL.GL import *


class Axis(object):

    def __init__(self):
        self.model = es.toGPUShape(bs.createAxis(1))
        self.show = True

    def toggle(self):
        self.show = not self.show

    def draw(self, pipeline, projection, view):
        if not self.show:
            return
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'model'), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(self.model, GL_LINES)
