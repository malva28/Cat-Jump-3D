"""
autor: Valentina Garrido
Main game module
"""

import glfw
from OpenGL.GL import *
import sys

import scene_graph_3D as sg

import easy_shaders as es
import lighting_shaders as ls
import  basic_shapes as bs
from model import *
from controller import Controller

import basic_shapes_extended as bs_ext
from models.Enemy import Enemy
from models.gameCameras import FollowCamera, FrontCamera, EagleCamera
from models.platforms.platform import FakePlatform
import lights as light
from models.staticViewObjects import Text3D

from ex_lighting_texture2 import createDice


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("Using the csv platform file from the homework example.")
        csv_file = "ex_structure.csv"
    else:
        csv_file = sys.argv[1]


    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 558
    height = 992

    window = glfw.create_window(width, height, 'Cat Jump 3D', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    #pipeline = es.SimpleModelViewProjectionShaderProgram()

    #texture_pipeline = es.SimpleTextureModelViewProjectionShaderProgram()

    lightShaderProgram = ls.SimpleTexturePhongShaderProgram()
    simpleLightShaderProgram = ls.SimplePhongShaderProgram()
    #lightShaderProgram = es.SimpleTextureGouraudShaderProgram()

    # Telling OpenGL to use our shader program
    #glUseProgram(texture_pipeline.shaderProgram)


    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Using the same view and projection matrices in the whole application
    projection = tr.perspective(45, float(width) / float(height), 0.1, 100)

    # TODO: use better camera classes
    # Generaremos diversas cámaras.
    static_view = tr.lookAt(
        np.array([0, 5, 0]),  # eye
        np.array([0, 0, 0]),  # at
        np.array([0, 0, 1])  # up
    )

    # HACEMOS LOS OBJETOS

    world = TextureScrollableWorld(csv_file)

    world.enable_game_over()

    controlador.set_model(world.mc)
    controlador.set_world(world)

    world.mc.model.set_shader(simpleLightShaderProgram)
    world.lose_cg.text_3D.set_shader(simpleLightShaderProgram)
    world.win_cg.text_3D.set_shader(simpleLightShaderProgram)


    t0 = 0

    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input

        # Calculamos el dt
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        world.update(dt, ti)



        glUseProgram(lightShaderProgram.shaderProgram)

        # Setting all uniform shader variables

        # region lighting texture
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Bright white for diffuse and specular components.
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ka"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform3f(glGetUniformLocation(lightShaderProgram.shaderProgram, "viewPosition"), 2.12132034, 2.12132034, 2.)
        glUniform1ui(glGetUniformLocation(lightShaderProgram.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(lightShaderProgram.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightShaderProgram.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightShaderProgram.shaderProgram, "quadraticAttenuation"), 0.01)
        # endregion

        # region lighting simple

        glUseProgram(simpleLightShaderProgram.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Bright white for diffuse and specular components.
        glUniform3f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "Ka"), 0.6, 0.6, 0.6)
        glUniform3f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform3f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "viewPosition"), 2.12132034, 2.12132034, 2.)
        glUniform1ui(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(simpleLightShaderProgram.shaderProgram, "quadraticAttenuation"), 0.01)
        # endregion

        world.draw(lightShaderProgram, projection)
        world.check_collisions()


        #text.draw(projection)



        glfw.swap_buffers(window)

    glfw.terminate()