"""
autor: Valentina Garrido
"""

import camera as cam
from mathlib import Point3 as _Point3
import numpy as np

import transformations as tr
from models.movingQuad import MovingQuad


class _GameCamera:
    "Abstract game camera class"
    def __init__(self, mc: MovingQuad = None):
        self.camera = None
        self.mc = mc
        self.mc_vz = 0.
        self.mc_theta = 0.
        self.mc_dtheta = 0.
        self.mc_vxy = 0.
        self.mc_vx = 0.
        self.mc_vy = 0.
        self.mc_turning = 0
        self.mc_x = 0.
        self.mc_y = 0.
        self.mc_z = 0.

    def update_mc_attrs(self):
        if self.mc is not None:
            self.mc_vz = self.mc.get_vel_z()
            self.mc_theta = self.mc.get_theta()
            self.mc_dtheta = self.mc.get_dtheta()
            self.mc_vxy = self.mc.get_vel_xy()
            self.mc_vx = self.mc.get_vel_x()
            self.mc_vy = self.mc.get_vel_y()
            self.mc_turning = self.mc.turning()
            self.mc_x = self.mc.get_pos_x()
            self.mc_y = self.mc.get_pos_y()
            self.mc_z = self.mc.get_pos_z()

    def follow_center(self, dt):
        pass

    def follow_eye(self, dt):
        pass

    def update(self, dt):
        self.update_mc_attrs()
        self.follow_center(dt)
        self.follow_eye(dt)

    def set_vel_to_zero(self, camera):
        camera.set_vel_move_x(0)
        camera.set_vel_move_y(0)
        camera.set_vel_move_z(0)

    def __str__(self):
        return str(self.camera)


class FrontCamera(_GameCamera):
    def __init__(self, mc: MovingQuad):
        super().__init__(mc)
        self.distance_from_mc = _Point3(0.,5.,1.)
        self.camera = cam.CameraXYZ(self.distance_from_mc)

    def follow_center(self, dt):
        self.camera.move_center_z(self.mc_vz * dt)

    def follow_eye(self, dt):
        self.camera.set_vel_move_z(self.mc_vz * dt)
        self.camera.move_z()

    def get_view(self):
        return self.camera.get_view()


class EagleCamera(_GameCamera):
    def __init__(self, mc: MovingQuad):
        super().__init__(mc)
        self.distance_from_mc = _Point3(0.,1.,4.)

        self.camera = cam.CameraXYZ(self.distance_from_mc, center= _Point3(0., 0., -1.))

    def follow_center(self, dt):
        self.camera.move_center_z(self.mc_vz * dt)

    def follow_eye(self, dt):
        self.camera.set_vel_move_z(self.mc_vz * dt)
        self.camera.move_z()

    def get_view(self):
        return self.camera.get_view()


class FollowCamera(_GameCamera):
    def __init__(self, mc: MovingQuad):
        super().__init__(mc)
        self.eye = np.zeros(3)
        self.distance_from_eye = 10.
        self.at = np.array([self.distance_from_eye, 0., 0.])
        self.up = np.array([0., 0., 1.])
        self.camera = cam.CameraXYZ(_Point3(0.,0.,0.), _Point3(1.,0.,0.))

    def follow_center(self, dt):
        turn_x = self.distance_from_eye * np.cos(self.mc_theta)
        turn_y = self.distance_from_eye * np.sin(self.mc_theta)

        self.at[0] = self.eye[0] + turn_x
        self.at[1] = self.eye[1] + turn_y
        self.at[2] = self.eye[2]

        #dx = self.mc_vx * dt
        #dy = self.mc_vy * dt
        #dz = self.mc.vz * dt

        #if self.mc_turning != 0:
        #    if self.mc_turning == 1:
        #        dtheta = self.mc_dtheta
        #    elif self.mc_turning == -1:
        #        dtheta = -self.mc_dtheta
        #    x = np.cos(self.mc_theta)
        #    y = np.sin(self.mc_theta)
        #
        #    dx += (x*(np.cos(dtheta)-1) - y*np.sin(dtheta))
        #    dy += (y*(np.cos(dtheta)-1) + x*np.sin(dtheta))

        #self.camera.move_center_x(dx)
        #self.camera.move_center_y(dy)
        #self.camera.move_center_z(dz)

    def follow_eye(self, dt):
        self.eye[0] = self.mc_x
        self.eye[1] = self.mc_y
        self.eye[2] = self.mc_z
        #vx = self.mc_vx*dt
        #vy = self.mc_vy*dt

        #self.camera.set_vel_move_x(vx)
        #self.camera.set_vel_move_y(vy)
        #self.camera.set_vel_move_z(self.mc.vz * dt)

        #self.camera.move_x()
        #self.camera.move_y()
        #self.camera.move_z()

    def get_view(self):
        return tr.lookAt(self.eye, self.at, self.up)


class StaticCamera(_GameCamera):
    def __init__(self):
        super().__init__(None)
        self.distance_from_mc = _Point3(0.,5.,0.)
        self.camera = cam.CameraXYZ(self.distance_from_mc)

    def follow_center(self, dt):
        pass

    def follow_eye(self, dt):
        pass

    def get_view(self):
        return self.camera.get_view()


class GameOverCamera(FrontCamera):
    def __init__(self, mc):
        super().__init__(mc)
        self.t = 0.

    def update(self, dt):
        super().update(dt)
        self.t += dt
        self.camera.rotate_center_z(3*np.pi*self.t)