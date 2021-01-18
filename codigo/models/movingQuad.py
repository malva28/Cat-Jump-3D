"""
autor: Valentina Garrido
"""

import scene_graph_3D as sg
from models.block import Block
from models.touchBlock import TouchBlock
from models.walls import Walls
from models.platforms.platformList import PlatformList
from withinEps import *

from typing import Optional


class MovingQuad(TouchBlock):
    def __init__(self, width: float, depth: float, height: float, quad_name: str = "Quad") -> None:
        super().__init__(width, depth, height, quad_name)
        self.set_state(Active())

        self.forward = False
        # forward indica si se mueve hacia en frente o no
        self.direc = 0
        self.theta = 0.
        self.dtheta = np.pi * 0.01
        # direc 0 indica que no gira, direc -1 indica que gira en sentido horario
        # y direc 1 indica que gira en sentido antihorario
        self.vxy = 0
        self.maxVel = 1
        self.dv = 1 / 40

        self.midair = False
        self.vz = 0
        self.maxVz = 2.5
        self.gravity = 1 / 20

        self.might_lose = False
        self.game_over = False
        self.won = False

        self.can_touch = True
        self.lives = 3
        self.temp_update_list = []
        self.invincible_timer = 1.5

    def set_state(self, state):
        self.state = state
        state.set_mc(self)

    def set_model(self, gpu_quad):
        super().set_model(gpu_quad)

        rot = sg.SceneGraphNode(self.name + "Rot")
        mc = sg.findNode(self.model, self.name)
        self.model.children = [rot]
        rot.children = [mc]

    def set_turn(self):
        rot = sg.findNode(self.model, self.name + "Rot")
        if self.direc == 1:
            sg.rotationZ(rot, self.dtheta)
        elif self.direc == -1:
            sg.rotationZ(rot, -self.dtheta)
        elif self.direc == 0:
            sg.rotationZ(rot, 0)

    def clamp_lower_lim_to(self, pz: float) -> None:
        self.pos_z = pz + self.width * 0.5

    def update_positions(self, dt: float) -> None:
        self.state.update_positions(dt)

    def update_mc_positions(self, dt):
        self.update_turn()
        self.set_turn()

        self.move()
        self.update_x(dt)
        self.update_y(dt)
        # print(self.pos_y)
        self.moveDown()
        self.pos_z += (self.vz * dt)

    def update_x(self, dt: float) -> None:
        self.pos_x += dt * self.get_vel_x()

    def update_y(self, dt: float) -> None:
        self.pos_y += dt * self.get_vel_y()

    def is_idle(self) -> bool:
        return not self.midair and within_eps(self.vxy, 0, self.dv)

    def sum_ang(self, ang: float):
        # theta goes from -pi to pi
        self.theta = (self.theta + ang) % (2 * np.pi)

    def update_turn(self):
        if self.direc == 1:
            self.sum_ang(self.dtheta)
        elif self.direc == -1:
            self.sum_ang(-self.dtheta)

    def move(self) -> None:
        if self.forward:
            self.move_forward()
        elif self.direc == 0:
            self.decelerate()

    def move_forward(self) -> None:
        if self.vxy <= self.maxVel:
            self.vxy += self.dv

    def decelerate(self) -> None:
        if self.vxy >= self.dv:
            self.vxy -= self.dv
        else:
            self.vxy = 0.0

    def horizontalCollide(self, walls: Walls) -> None:
        if (walls.leftCollide(self) and (self.theta > np.pi / 2 and self.theta < 3 * np.pi / 2)) or \
                (walls.rightCollide(self) and (self.theta < np.pi / 2 or self.theta > 3 * np.pi / 2)) or \
                (walls.frontCollide(self) and self.theta < np.pi) or (walls.backCollide(self) and self.theta > np.pi):
            self.vxy = 0.0

        # else:
        #    self.allowLeftMove = True
        #    self.allowRightMove =True

    def jump(self) -> None:
        if not self.midair:
            self.midair = True
            self.vz = self.maxVz

    def jump_state(self) -> int:
        # returns 1 if it's going up, 2 if it's floating
        # 3 if it's going down, and 0 if neither of them
        if not self.midair:
            return 0
        else:
            if self.vz > self.maxVz / 5:
                return 1
            elif self.vz < self.maxVz / 5 and self.vz > -self.maxVz / 5:
                return 2
            else:
                return 3

    def moveDown(self) -> None:
        if self.midair:
            self.vz -= self.gravity

    def verticalCollide(self, platforms: PlatformList) -> Optional[int]:
        for i in range(platforms.len_p):
            row = platforms.platforms[i]
            for p in row:
                if p.upperCollide(self):
                    self.midair = False
                    self.vz = 0.0
                    self.clamp_lower_lim_to(p.upperLim())
                    return i
                else:
                    self.midair = True
        return None

    def efficientVerticalCollide(self, platforms: PlatformList, i_row: int) -> Optional[int]:
        if i_row < 0:
            i_row = 0
        if i_row >= platforms.len_p:
            i_row = platforms.len_p - 1

        row = platforms.platforms[i_row]
        for p in row:
            if p.upperCollide(self):
                self.midair = False
                self.vz = 0.0
                self.clamp_lower_lim_to(p.upperLim())
                return i_row
            else:
                self.midair = True
        return None

    def enemy_collide(self, enemy_list):
        for enemy in enemy_list.get_active_enemies():
            enemy.in_boundary(self)

    def update_losing_status(self, platforms: PlatformList, recent_i_row: int) -> Optional[bool]:
        if not self.might_lose:
            if platforms.len_p == 0 or not recent_i_row:
                return
            if platforms.len_p < 1:
                if recent_i_row == platforms.len_p:
                    self.might_lose = True
            else:
                if recent_i_row > 1:
                    self.might_lose = True

    def stop_movement(self):
        self.forward = False
        self.direc = 0
        self.theta = 0.
        self.vxy = 0

        self.midair = False
        self.vz = 0

    def flicker(self, dt):
        delta_flick = 3
        delta = delta_flick * dt
        decision = np.floor(self.invincible_timer / delta)
        if decision % 2 == 0:
            self.disable_drawing()
        else:
            self.enable_drawing()
        self.invincible_timer -= dt

    def update(self, t, dt):
        if self.invincible_timer > 0.:
            self.flicker(dt)
        else:
            self.temp_update_list.remove(self)
            self.enable_drawing()
            self.can_touch = True

    def on_enemy_touch(self, enemy):
        self.lives -= 1
        self.can_touch = False
        self.invincible_timer = 1.5

        if self.lives >= 0.:
            self.notify_life_reduce()
        if self.lives <= 0:
            self.game_over = True
            self.on_game_over()
            self.notify_game_lost()

    def on_yarn_touch(self, yarn):
        self.game_over = True
        self.won = True
        self.on_game_over()
        self.notify_game_won()

    def make_inactive(self):
        self.stop_movement()
        self.state.make_inactive()

    def on_game_over(self):
        self.make_inactive()
        self.game_over = True
        self.notify_game_over()


    def notify_life_reduce(self):
        for obs in self._observers:
            obs.on_life_reduce(self)

    def notify_game_over(self):
        for obs in self._observers:
            obs.on_game_over(self)

    def notify_game_lost(self):
        for obs in self._observers:
            obs.on_lose(self)

    def notify_game_won(self):
        for obs in self._observers:
            obs.on_win(self)


    # region getters

    def get_vel_z(self):
        return self.vz

    def get_theta(self):
        return self.theta

    def get_dtheta(self):
        return self.dtheta

    def get_vel_xy(self):
        return self.vxy

    def get_vel_x(self):
        return self.vxy * np.cos(self.theta)

    def get_vel_y(self):
        return self.vxy * np.sin(self.theta)

    def get_pos_x(self):
        return self.pos_x

    def get_pos_y(self):
        return self.pos_y

    def get_pos_z(self):
        return self.pos_z

    def turning(self):
        return self.direc

    # endregion


class State:
    def __init__(self):
        self.mc = None

    def set_mc(self, mc):
        self.mc = mc

    def change_state(self, state):
        self.mc.set_state(state)

    def update_positions(self, dt):
        pass

    def make_inactive(self):
        pass

    def is_active(self):
        return False

    def is_inactive(self):
        return False


class Active(State):
    def update_positions(self, dt: float) -> None:
        self.mc.update_mc_positions(dt)

    def make_inactive(self):
        self.change_state(Inactive())


    def is_active(self):
        return True


class Inactive(State):
    def is_inactive(self):
        return True


class MCListener:
    def __init__(self):
        pass

    def on_life_reduce(self, mc):
        pass

    def on_game_over(self, mc):
        pass

    def on_lose(self, mc):
        pass

    def on_win(self, mc):
        pass

