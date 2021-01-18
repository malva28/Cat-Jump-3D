"""
autor: Valentina Garrido
"""

import scene_graph_3D as sg
import easy_shaders as es
import basic_shapes as bs
import transformations as tr
import numpy as np

import basic_shapes_extended as bs_ext
import lighting_shaders as ls

from models.block import Block
import scene_graph_3D as sg
from models.gameCameras import StaticCamera
from models.movingQuad import MCListener
from textureSphere import generateSemiSphereTextureNormals
from sprites3D import create_3D_sprite_single_color

from OpenGL.GL import GL_REPEAT, GL_NEAREST


class StaticViewObject:
    def __init__(self):
        self.model = None
        self.static_cam = StaticCamera()

    def draw(self, projection, pipeline=None):
        if self.model:
            sg.drawSceneGraphNode(self.model, projection, self.static_cam.get_view(), pipeline=pipeline)


class GameOverCG(StaticViewObject):
    def __init__(self):
        super().__init__()
        gameOverPic = sg.SceneGraphNode("GameOverPic")
        gameOverPic.transform = tr.matmul([tr.translate(0, 0.5, 0),
                                           tr.scale(1.8, 1.8 * 200 / 150, 1)])

        gameOverText = sg.SceneGraphNode("GameOverText")
        gameOverText.transform = tr.scale(1.8, 1.8 * 15 / 100, 1)

        gameOverTextRot = sg.SceneGraphNode("GameOverTextRot")
        gameOverTextRot.children += [gameOverText]

        gameOverTextTR = sg.SceneGraphNode("GameOverTextTR")
        gameOverTextTR.transform = tr.translate(0, 2, 0)
        gameOverTextTR.children += [gameOverTextRot]

        gameOver = sg.SceneGraphNode("GameOver")
        gameOver.children += [gameOverPic, gameOverTextTR]

        self.pause = 1.0
        self.model = gameOver

    def soft_rotate(self, t, min_angle=-np.pi / 4, max_angle=np.pi / 4):
        resulting_angle = min_angle + (max_angle - min_angle) * np.sin(t)
        return resulting_angle

    def update(self, t, dt):
        self.animation(t, dt)

    def animation(self, t, dt):
        pass

    def set_picture(self, filename):
        gpu_pic = es.toGPUShape(bs_ext.create4VertexTextureNormal(filename, [-0.5,0.,-0.5], [0.5,0.,-0.5],
                                                                  [0.5,-0.5,0.5], [-0.5,0,0.5], nx=1, ny=1), GL_REPEAT, GL_NEAREST)
        gameOverPic = sg.findNode(self.model, "GameOverPic")
        sg.translate(gameOverPic, 0,1.6,0)
        sg.scale(gameOverPic,1,1,2.5)
        gameOverPic.children += [gpu_pic]

    def set_text(self, phrase):
        self.text_3D = Text3D(phrase)
        self.model.children += [self.text_3D.model]
        #gpu_pic = es.toGPUShape(bs.createTextureNormalsCube(filename), GL_REPEAT, GL_NEAREST)
        #gameOverText = sg.findNode(self.model, "GameOverText")
        #gameOverText.children += [gpu_pic]


class WinCG(GameOverCG):
    def __init__(self):
        super().__init__()
        self.set_picture("textures/gameWonPic.png")
        self.set_text("you win")
        self.text_3D.read_letters([{'r': 1., 'g': 0., 'b': 0.},{'r': 1., 'g': 1., 'b': 0.},
                                   {'r': 0., 'g': 1., 'b': 0.},{'r': 0., 'g': 0., 'b': 0.},
                                   {'r': 0., 'g': 1., 'b': 1.},{'r': 0., 'g': 0., 'b': 1.},
                                   {'r': 1., 'g': 0., 'b': 1.}])

        self.reset_timers()
        self.rotation_delay = 0.2
        self.rotations_left = np.zeros(len(self.text_3D.letters), dtype=float)
        sg.uniformScale(self.text_3D.model, 0.6)
        sg.translate(self.text_3D.model, 0., 2., 1)

        #gameOverPic = sg.findNode(self.model, "GameOverPic")
        #gameOverPic.drawing = False

    def animation(self, t, dt):
        dtheta = 2 * np.pi / len(self.text_3D)
        for i in range(len(self.text_3D.letters)):
            letter_tr = self.text_3D.letters[i]
            offset = t + (dtheta * i)
            animation_vel = 7
            letter_tr.transform = tr.uniformScale(0.8 + 0.5 * np.fabs(np.sin(animation_vel*offset)))
        self.timer_for_next_rotation -= dt

        if self.timer_for_next_rotation <= 0.:
            if not self.rotating:
                self.rotations_left = np.ones(len(self.text_3D.letters), dtype=float) * 2 * np.pi
                self.rotating = True
            self.rotate_each_letter(dt, self.rotations_left)

    def rotate_each_letter(self, dt, rotations_left):
        # rotations_left = np.ones(len(self.text_3D.letters), dtype=float)*2*np.pi
        if not np.all(rotations_left <= 0.):
            n = len(self.text_3D.letters)
            decision = int(np.floor(self.time_rotating / self.rotation_delay))
            max_n = decision if decision < n else n
            for i in range(max_n):
                letter = self.text_3D.letters[i]
                rotation_left = self.rotate_letter(dt, letter, rotations_left[i])
                rotations_left[i] = rotation_left
            self.time_rotating += dt
        else:
            self.reset_timers()

    def reset_timers(self):
        self.timer_for_next_rotation = 5.
        self.time_rotating = 0.
        self.rotating = False

    def rotate_letter(self, dt, letter_node, rotation_left=2 * np.pi):
        if rotation_left > 0.:
            dangle = np.pi/2
            # print(self.timer_for_next_rotation)
            # print(self.time_rotating)
            # print("dangle: ", dangle)
            # print("dt:", dt)

            dtheta = dt * dangle
            inner_letter_node = sg.findNode(letter_node, "letter")
            if rotation_left - dtheta < 0.:
                sg.rotationZ(inner_letter_node, rotation_left)
            else:
                sg.rotationZ(inner_letter_node, dtheta)
            rotation_left -= dtheta
        return rotation_left


class LoseCG(GameOverCG):
    def __init__(self):
        super().__init__()
        self.set_picture("textures/gameOverPic.png")
        self.set_text("you lost")
        self.text_3D.read_letters([{'r':0.5, 'g':0., 'b':1.}], 0.5)

        self.reset_timers()
        self.rotation_delay = 0.2
        self.rotations_left = np.zeros(len(self.text_3D.letters), dtype=float)
        sg.uniformScale(self.text_3D.model, 0.6)
        sg.translate(self.text_3D.model,0.,2.,1)

    #def update(self, t, dt):
    #    self.animation(t, dt)
    #    if self.timer_for_next_rotation <= 0.:

    def animation(self, t, dt):
        dtheta = 2*np.pi/len(self.text_3D)
        for i in range(len(self.text_3D.letters)):
            letter_tr = self.text_3D.letters[i]
            offset = t+(dtheta*i)
            letter_tr.transform = tr.uniformScale(1+0.2*np.sin(offset))
        self.timer_for_next_rotation -= dt

        if self.timer_for_next_rotation <= 0.:
            if not self.rotating:
                self.rotations_left = np.ones(len(self.text_3D.letters), dtype=float) * 2 * np.pi
                self.rotating = True
            self.rotate_each_letter(dt, self.rotations_left)

    def rotate_each_letter(self, dt, rotations_left):
        #rotations_left = np.ones(len(self.text_3D.letters), dtype=float)*2*np.pi
        if not np.all(rotations_left <= 0.):
            n = len(self.text_3D.letters)
            decision = int(np.floor(self.time_rotating/self.rotation_delay))
            max_n = decision if decision < n else n
            for i in range(max_n):
                letter = self.text_3D.letters[i]
                rotation_left = self.rotate_letter(dt, letter, rotations_left[i])
                rotations_left[i] = rotation_left
            self.time_rotating += dt
        else:
            self.reset_timers()

    def reset_timers(self):
        self.timer_for_next_rotation = 5.
        self.time_rotating = 0.
        self.rotating = False


    def rotate_letter(self, dt, letter_node, rotation_left = 2*np.pi):
        if rotation_left > 0.:
            dangle = np.pi/2
            #print(self.timer_for_next_rotation)
            #print(self.time_rotating)
            #print("dangle: ", dangle)
            #print("dt:", dt)

            dtheta = dt*dangle
            inner_letter_node = sg.findNode(letter_node, "letter")
            if rotation_left - dtheta < 0.:
                sg.rotationX(inner_letter_node, rotation_left)
            else:
                sg.rotationX(inner_letter_node, dtheta)
            rotation_left -= dtheta
        return rotation_left


class Text3D(StaticViewObject):
    def __init__(self, text_phrase, shader=None):
        super().__init__()
        self.phrase = text_phrase
        self.letters = []
        self.model = sg.SceneGraphNode("phrase")

        self.len_phrase = len(text_phrase)

        self.set_shader(shader)

    def __len__(self):
        return self.len_phrase

    def set_shader(self, shader=None):
        self.model.shader = shader

    def read_letters(self, colors, letter_depth=0.5):
        base_file = "textures/letters/letter_{}.png"

        dsize = 2/len(self.phrase)

        for i in range(len(self)):
            letter = self.phrase[i]
            if letter != " ":
                if len(colors) == 1:
                    color = colors[0]
                else:
                    color = colors[i]

                img_name = base_file.format(letter)

                letterShape = create_3D_sprite_single_color(img_name, color, letter_depth)
                gpuLetter = es.toGPUShape(letterShape)

                letter_node = sg.SceneGraphNode("letter")
                letter_node.children = [gpuLetter]

                sg.uniformScale(letter_node, dsize)
                sg.rotationY(letter_node, np.pi / 2)

                letter_pos = sg.SceneGraphNode("letterPos")
                letter_pos.children = [letter_node]

                sg.translate(letter_pos, dsize*(i+0.5)-1, 0., 0.)

                letter_tr = sg.SceneGraphNode("letterTR")
                letter_tr.children = [letter_pos]

                self.model.children += [letter_tr]

                self.letters.append(letter_tr)

        sg.scale(self.model, -1, 1, 1)




class LifeGauge(StaticViewObject, MCListener):
    def __init__(self, ini_pos_x, ini_pos_z):
        super().__init__()
        self.pos_x = ini_pos_x
        self.pos_z = ini_pos_z
        self.name = "LifeGauge"

        self.current_life_sprite = 0
        self.sprites = []

        lifeGauge = sg.SceneGraphNode(self.name)
        sg.rotationX(lifeGauge, np.pi/2)
        sg.uniformScale(lifeGauge, 0.2)

        lifeGaugeTR = sg.SceneGraphNode(self.name+"TR")
        sg.translate(lifeGaugeTR, self.pos_x, 1.8, self.pos_z)
        lifeGaugeTR.children += [lifeGauge]

        self.model = lifeGaugeTR

        self.default_sprite()

    def load_sprites(self):
        filenames = ["textures/crying.png",
                     "textures/slight_frown.png",
                     "textures/slight_smile.png",
                     "textures/smiley.png"]
        self.sprites = [es.toGPUShape(generateSemiSphereTextureNormals(img, 20, 20), GL_REPEAT, GL_NEAREST)
                        for img in filenames]

    def set_sprite(self, gpu_sprite):
        lifeGauge = sg.findNode(self.model, self.name)
        lifeGauge.children = [gpu_sprite]

    def default_sprite(self):
        self.current_life_sprite = 3
        self.load_sprites()
        self.change_life_display(self.current_life_sprite)

    def change_life_display(self, ind):
        if ind >= 0 and ind < len(self.sprites):
            self.current_life_sprite = ind
            sprite = self.sprites[self.current_life_sprite]
            self.set_sprite(sprite)

    def on_life_reduce(self, mc):
        self.change_life_display(self.current_life_sprite-1)

    def on_lose(self, mc):
        self.change_life_display(0)

    def on_win(self, mc):
        self.change_life_display(3)


