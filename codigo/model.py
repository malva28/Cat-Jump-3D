"""
autor: Valentina Garrido
"""

import transformations as tr
import scene_graph_3D as sg
import numpy as np

from models.Enemy import EnemyGenerator
from models.gameCameras import EagleCamera, FollowCamera, FrontCamera, GameOverCamera
from models.platforms.platformFactory import PlatformFactory
from models.platforms.platformList import PlatformList
from models.movingQuad import MovingQuad, MCListener
from models.staticViewObjects import LifeGauge, LoseCG, WinCG
from models.walls import Walls
from models.background import Background
from models.base import Base
from models.platforms.platform import Platform
from models.cat import Cat
from models.yarn import Yarn

import camera as cam
from mathlib import Point3 as _Point3


FRONT_CAMERA = 0
EAGLE_CAMERA = 1
FOLLOW_CAMERA = 2


class ScrollableWorld(MCListener):
    def __init__(self, platform_filename, z_sep, window_width= 558, window_height = 992):
        self.window_w = window_width
        self.window_h = window_height
        self.platform_filename = platform_filename

        self.mc = None
        self.base = None
        self.yarn = None

        self.platforms = None
        self.walls = Walls(-1, 1, -1.6, 1.6)

        self.world = sg.SceneGraphNode("World")
        self.not_moving = sg.SceneGraphNode("StaticObjs")
        self.world.children += [self.not_moving]
        self.update_list = []
        self.static_draw_list =[]

        self.z_sep = z_sep
        self.min_scroll_z = 0.0
        self.max_scroll_z = 1.0
        self.scrolling = -1
        self.fixed_ratio = False
        self.reduced_visibility = False

        self.selected_camera = None

    def get_number_of_plat_rows(self):
        return self.platforms.len_p

    def set_mc(self, mc):
        self.mc = mc
        self.world.children += [self.mc.model]

    def set_cameras(self):
        self.cameras = [FrontCamera(self.mc),
                        EagleCamera(self.mc),
                        FollowCamera(self.mc),
                        GameOverCamera(self.mc)]

    def change_camera(self, camera_constant=FRONT_CAMERA):
        self.selected_camera = self.cameras[camera_constant]

    def platform_row_mc_is_near_to(self):
        y = self.mc.lowerLim()
        i_row = int(np.ceil((y+0.5) / self.z_sep))
        return i_row

    def set_platforms(self, platform_list):
        self.platforms = platform_list
        self.platforms.read_from_csv(self.platform_filename)
        self.platforms.position_platforms(self.platforms.presence)

        self.platforms.update_model_tree()
        self.max_scroll_z = self.platforms.maximum_height() - 2

    def add_platforms_to_model(self):
        self.not_moving.children += [self.platforms.model]

    def set_yarn(self, yarn):
        yarn_pos_z = self.platforms.maximum_height() + self.z_sep - 1
        yarn.set_init_pos(0.0, 0.0, yarn_pos_z)
        #yarn.set_init_pos(0.5, 0.5, 0.0)
        yarn.update_translate_matrix()

        self.yarn = yarn
        self.yarn.add_observer(self.mc)
        #self.yarn.add_observer(self)
        self.not_moving.children += [yarn.model]

    def dummy_platform_test(self, platform_list):
        self.platforms = platform_list

        ones = np.array([[1, 0, 0] for i in range(30)], dtype=int)
        self.platforms.read_platforms(ones)
        self.platforms.position_platforms(ones)

        self.platforms.update_model_tree()
        self.max_scroll_z = self.platforms.maximum_height() - 2

    def fix_bottom(self):
        if self.window_h > self.window_w:
            factor = self.window_w/self.window_h
            return tr.translate(0,-(1-factor),0)

    def fix_ratio(self):
        if self.window_h > self.window_w:
            factor = self.window_w/self.window_h
            self.world.transform = tr.matmul([tr.translate(0,-(1-factor),0),
                tr.scale(1, factor, 1)])
            self.fixed_ratio = True

    def update_mc(self, dt):
        # updates mc's position and
        # sets scrolling to 1 if it should scroll, -1 if mc is mc is under
        # scrolling limits and 0 if mc it's over scrolling limits

        self.mc.update_positions(dt)
        if self.mc.pos_z > self.min_scroll_z and self.mc.pos_z < self.max_scroll_z:
            self.scrolling = 1
        elif self.mc.pos_z > self.max_scroll_z:
            self.scrolling = 0
        else:
            self.scrolling = -1

    def camera_update(self, dt):
        [c.update(dt) for c in self.cameras]


    def visible_slabs(self):
        i_row = self.platform_row_mc_is_near_to()
        w_range = self.get_current_y_view()
        row_min = int(np.ceil((w_range[0] + 1) / self.z_sep))
        row_max = int(np.ceil((w_range[1] + 1) / self.z_sep))

        # uncomment this for visibility of only the current slab level
        #return [i_row, i_row + 1]

        return [i_row-1, i_row+2]



    def update(self, dt, t):
        self.update_mc(dt)
        self.camera_update(dt)
        self.yarn.grow_and_shrink(dt)

        [o.update(t, dt) for o in self.update_list]

        if self.reduced_visibility:
            slab_range = self.visible_slabs()
            self.platforms.update_model_tree(slab_range[0], slab_range[1])
        else:
            self.platforms.update_model_tree()

        self.enemy_generator.create_enemy()
        self.enemy_generator.update(dt)

        self.no_scroll()
        #if self.scrolling == 1:
        #    self.verticalScroll(dt)
        #else:
        #    self.no_scroll()

    def get_current_y_view(self):
        factor = self.window_h/self.window_w
        lower_z = -1
        upper_z = 1
        if self.scrolling == -1:
            if self.fixed_ratio:
                return [lower_z, upper_z + 2 * (factor - 1)]
            else:
                return [lower_z, upper_z]
        elif self.scrolling == 1:
            if self.fixed_ratio:
                return [lower_z + self.mc.pos_z,
                        upper_z + self.mc.pos_z + 2 * (factor-1)]
            else:
                return [lower_z + self.mc.pos_z, upper_z + self.mc.pos_z]
        else:
            if self.fixed_ratio:
                return [self.max_scroll_z + lower_z,
                        self.max_scroll_z + upper_z + 2 * (factor - 1)]
            else:
                return [self.max_scroll_z + lower_z,
                        self.max_scroll_z + upper_z]

    def no_scroll(self):
        self.mc.update_translate_matrix()
        #if self.scrolling == -1:
        #    self.mc.update_translate_matrix()
        #elif self.scrolling == 0:
        #    self.camera.set_vel_move_x(0)
        #    self.camera.set_vel_move_y(0)
        #    self.camera.set_vel_move_z(0)
            # self.mc.model.transform = tr.translate(self.mc.pos_x, self.mc.pos_y - self.max_scroll_y, 0)
            # self.not_moving.transform = tr.translate(0, -self.max_scroll_y, 0)

    def verticalScroll(self, dt):
        pass
        #self.mc.update_translate_matrix()

        # self.mc.model.transform = tr.translate(self.mc.pos_x, 0, 0)
        # self.not_moving.transform = tr.translate(0,-self.mc.pos_y,0)

    def draw(self, pipeline, projection, view = None):
        if not view:
            view = self.selected_camera.get_view()
        sg.drawSceneGraphNode(self.world, projection, view, pipeline)
        self.enemy_generator.draw(pipeline, projection, view)

        [o.draw(projection, pipeline) for o in self.static_draw_list]

    def check_collisions(self):
        self.mc.enemy_collide(self.enemy_generator)
        self.mc.horizontalCollide(self.walls)
        row_i = self.platform_row_mc_is_near_to()

        stepped_into_row_i = self.mc.efficientVerticalCollide(self.platforms, row_i)

        #if row_i >= self.platforms.len_p:
        self.yarn.update_winning_status(self.mc)
        # stepped_into_row        print(row_i)_i = self.mc.verticalCollide(self.platforms)

        self.mc.update_losing_status(self.platforms, stepped_into_row_i)

    def enable_game_over(self):
        self.base.enable_game_over = True
        self.yarn.enable_game_over = True

    def on_fake_platform_collision(self, platform):
        self.update_list.append(platform)

    def on_enemy_touch(self, enemy):
        self.mc.temp_update_list = self.update_list
        self.update_list.append(self.mc)

    def on_game_over(self, mc):
        self.enemy_generator.generate = False
        self.change_camera(3)


    def on_lose(self, mc):
        self.static_draw_list.append(self.lose_cg)
        self.update_list.append(self.lose_cg)

    def on_win(self, mc):
        self.static_draw_list.append(self.win_cg)
        self.update_list.append(self.win_cg)



class NoTextureScrollableWorld(ScrollableWorld):
    def __init__(self, platform_filename, y_sep=0.8, window_width= 558, window_height = 992):
        super().__init__(platform_filename,y_sep, window_width, window_height)

        mc = MovingQuad(0.2, 0.2, "Quad")
        mc.set_model_color((0.0, 0.0, 0.0))

        base = Base()
        base.set_model_color((0.0, 1.0, 1.0))
        self.base = base

        slab_pattern = Platform(0.4,  0.1)
        slab_pattern.set_model_color((1.0, 0.0, 0.0))

        platform_list = PlatformList(base,slab_pattern,y_sep)

        yarn = Yarn(0.3)
        yarn.set_model_color((1.0, 1.0, 0.0))


        self.set_mc(mc)
        self.set_platforms(platform_list)
        self.add_platforms_to_model()
        self.set_yarn(yarn)


class TextureScrollableWorld(ScrollableWorld):
    def __init__(self, platform_filename, y_sep=0.8, window_width= 558, window_height = 992):
        super().__init__(platform_filename, y_sep, window_width, window_height)

        mc = Cat(0.2, 0.04, 0.2)

        factory = PlatformFactory(0.4, 0.4, 0.1, self, timer=3., gravity=1/20)

        base = Base()
        base.set_model_texture("textures/base.png")
        self.base = base

        platform_list = PlatformList(base, factory, y_sep)
        platform_list.set_texture("textures/platform.png")

        yarn = Yarn(0.2)
        yarn.set_model_texture("textures/lana.png")

        self.set_mc(mc)
        self.set_cameras()
        self.change_camera()

        self.set_platforms(platform_list)

        self.background = None
        self.set_background()
        self.add_platforms_to_model()
        self.set_yarn(yarn)

        self.yarn.set_bg(self.background)
        self.yarn.set_world_model(self.world)
        self.yarn.set_update_list(self.update_list)

        self.base.set_bg(self.background)
        self.base.set_world_model(self.world)
        self.base.set_update_list(self.update_list)

        self.enemy_generator = EnemyGenerator(self.z_sep, self.get_number_of_plat_rows())
        self.enemy_generator.set_texture("textures/moth.png")
        self.enemy_generator.set_observers(self, self.mc)
        self.enemy_generator.init_enemies()

        self.lives = LifeGauge(-0.5, 1.1)
        self.static_draw_list.append(self.lives)

        self.lose_cg = LoseCG()
        self.win_cg = WinCG()

        self.mc.add_observer(self.lives)
        self.mc.add_observer(self)

        # self.mc.add_observer(self.base)



    def set_background(self):
        self.background = Background(self.window_w, self.window_h, self.max_scroll_z)
        self.not_moving.children += [self.background.model]
