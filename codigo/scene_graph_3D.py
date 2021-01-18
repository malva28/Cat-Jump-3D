# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
A simple scene graph class and functionality
"""

from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import copy

import transformations as tr
import easy_shaders as es

import basic_shapes_extended as bs_ext
from tr_commands import *

from typing import Optional


# A simple class to handle a scene graph
# Each node represents a group of objects
# Each leaf represents a basic figure (GPUShape) (AdvancedGPUShape)
# To identify each node properly, it MUST have a unique name
class SceneGraphNode:
    def __init__(self, node_name: str) -> None:
        self.name = node_name
        self.transform = tr.identity()
        self.children = []
        self.drawing = True
        self.shader = None

    def set_shader(self, shader):
        self.shader = shader


def translate(node: SceneGraphNode, tx: float = 0, ty: float = 0, tz: float = 0) -> None:
    exec_and_transform(node, Command.TRANSLATE, tx, ty, tz)


def scale(node, sx=1, sy=1, sz=1):
    exec_and_transform(node, Command.SCALE, sx, sy, sz)


def uniformScale(node, s=1):
    exec_and_transform(node, Command.UNIFORM_SCALE, s)


def rotationX(node, theta=0):
    exec_and_transform(node, Command.ROTATION_X, theta)


def rotationY(node, theta=0):
    exec_and_transform(node, Command.ROTATION_Y, theta)


def rotationZ(node, theta=0):
    exec_and_transform(node, Command.ROTATION_Z, theta)


def rotationA(node, theta=0):
    exec_and_transform(node, Command.ROTATION_A, theta)


def shearing(node, xy=0, yx=0, xz=0, zx=0, yz=0, zy=0):
    exec_and_transform(node, Command.SHEARING, xy, yx, xz, zx, yz, zy)


def exec_and_transform(node, command, *params):
    tr_matrix = command_dictionary[command](*params)
    node.transform = tr.matmul([tr_matrix, node.transform])

    execute_transform(node, command, *params)


def execute_transform(node, command, *params):
    if len(node.children) == 1 and isinstance(node.children[0], es.GPUShape):
        return

    if len(node.children) == 1 and isinstance(node.children[0], bs_ext.AdvancedGPUShape):
        leaf = node.children[0]
        leaf.execute(command, *params)

    else:
        for child in node.children:
            execute_transform(child, command, *params)


def findNode(node: SceneGraphNode, node_name: str) -> Optional[SceneGraphNode]:
    # The name was not found in this path
    if isinstance(node, es.GPUShape) or isinstance(node, bs_ext.AdvancedGPUShape):
        return None

    # This is the requested node
    if node.name == node_name:
        return node

    # All childs are checked for the requested name
    for child in node.children:
        foundNode = findNode(child, node_name)
        if foundNode != None:
            return foundNode

    # No child of this node had the requested name
    return None


def copyNode(node):
    if isinstance(node, es.GPUShape):
        return node

    if isinstance(node, bs_ext.AdvancedGPUShape):
        return node.clone()

    copiedNode = SceneGraphNode(node.name)
    copiedNode.transform = copy.deepcopy(node.transform)

    for child in node.children:
        copiedNode.children += [copyNode(child)]
    return copiedNode


def findTransform(node, name, parentTransform=tr.identity()):
    # The name was not found in this path
    if isinstance(node, es.GPUShape):
        return None

    newTransform = np.matmul(parentTransform, node.transform)

    # This is the requested node
    if node.name == name:
        return newTransform

    # All childs are checked for the requested name
    for child in node.children:
        foundTransform = findTransform(child, name, newTransform)
        if isinstance(foundTransform, (np.ndarray, np.generic)):
            return foundTransform

    # No child of this node had the requested name
    return None


def findPosition(node, name, parentTransform=tr.identity()):
    foundTransform = findTransform(node, name, parentTransform)

    if isinstance(foundTransform, (np.ndarray, np.generic)):
        zero = np.array([[0, 0, 0, 1]], dtype=np.float32).T
        foundPosition = np.matmul(foundTransform, zero)
        return foundPosition

    return None


def drawSceneGraphNode(node: SceneGraphNode, projection: np.ndarray, view: np.ndarray, pipeline=None,
                       parentTransform: np.ndarray = tr.identity()) -> None:
    assert (isinstance(node, SceneGraphNode))

    if node.drawing:

        if node.shader is not None:
            pipeline = node.shader

        # Composing the transformations through this path
        newTransform = np.matmul(parentTransform, node.transform)

        # If the child node is a leaf, it should be a GPUShape.
        # Hence, it can be drawn with drawShape
        if len(node.children) == 1 and isinstance(node.children[0], es.GPUShape):
            leaf = node.children[0]
            glUseProgram(pipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'model'), 1, GL_TRUE, newTransform)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'projection'), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, 'view'), 1, GL_TRUE, view)

            # dunno why here it used to be "transform" instead of "model
            # glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, transformName), 1, GL_TRUE, newTransform)
            pipeline.drawShape(leaf)

        elif len(node.children) == 1 and isinstance(node.children[0], bs_ext.AdvancedGPUShape):
            leaf = node.children[0]
            leaf.draw(view, projection, shader=pipeline)
        # If the child node is not a leaf, it MUST be a SceneGraphNode,
        # so this draw function is called recursively
        else:
            for child in node.children:
                drawSceneGraphNode(child, projection, view, pipeline, newTransform)
