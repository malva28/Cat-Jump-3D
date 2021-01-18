import glfw
import sys

from models.movingQuad import MovingQuad, MCListener

from model import FRONT_CAMERA, EAGLE_CAMERA, FOLLOW_CAMERA


class Controller(MCListener):
    def __init__(self) -> None:
        self.mc = None
        self.game_over = False

    def set_model(self, m: MovingQuad) -> None:
        self.mc = m

    def set_world(self, world):
        self.world = world

    def on_key(self, window, key, scancode, action, mods):
        if self.game_over:
            print("The game is over!"
                  "\nRerun the program to start again")
            return

        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        elif key == glfw.KEY_A and action == glfw.PRESS:
            self.mc.direc = -1

        elif key == glfw.KEY_D and action == glfw.PRESS:
            self.mc.direc = 1

        elif (key == glfw.KEY_A or key == glfw.KEY_D) and action == glfw.RELEASE:
            self.mc.direc = 0

        elif key == glfw.KEY_W and action == glfw.PRESS:
            self.mc.forward = True

        elif key == glfw.KEY_W and action == glfw.RELEASE:
            self.mc.forward = False

        elif key == glfw.KEY_B and action == glfw.PRESS:
            self.world.change_camera(FRONT_CAMERA)
            self.world.reduced_visibility = False
            self.mc.enable_drawing()

        elif key == glfw.KEY_N and action == glfw.PRESS:
            self.world.change_camera(EAGLE_CAMERA)
            self.world.reduced_visibility = True
            self.mc.enable_drawing()

        elif key == glfw.KEY_M and action == glfw.PRESS:
            self.world.change_camera(FOLLOW_CAMERA)
            self.world.reduced_visibility = False
            self.mc.disable_drawing()

        elif key == glfw.KEY_SPACE:
            self.mc.jump()

        else:
            print('Unknown key')

    def on_game_over(self, mc):
        self.game_over = True
