"""
autor: Valentina Garrido
"""

import csv
import numpy as np

from models.platforms.platformFactory import PlatformFactory
import scene_graph_3D as sg


class PlatformList:
    def __init__(self, base, platform_factory: PlatformFactory, y_sep=0.5, name="Platforms"):
        self.z_sep = y_sep  # platform to platform separation in y axis

        self.platform_factory = platform_factory

        base.update_init_pos()
        self.platforms = [[base]]
        self.len_p = 1
        self.presence = []
        self.x_positions = [-0.7, -0.35, 0.0, 0.35, 0.7]
        self.n_plats = 5
        self.y_positions = [-0.35, 0.35]
        self.name = name

        platform_list = sg.SceneGraphNode(self.name)
        self.model = platform_list

    def set_texture(self, texture_filename):
        self.platform_factory.set_texture(texture_filename)

    def read_from_csv(self, structure_csv):
        with open(structure_csv, newline='') as fout:
            reader = csv.reader(fout)
            rows = []
            for row in reader:
                new_row = []
                for ele in row:
                    if ele == "x":
                        ele = -1
                    new_row.append(ele)
                rows.append(new_row)

            arr = np.array(rows, dtype=int)
            self.presence = arr
            self.read_platforms(arr)

    def read_platforms(self, presence_array):
        len_p = 1
        for rows in presence_array:
            platform_row = []
            for present in rows:
                if present:
                    if present == -1:
                        new_plat = self.platform_factory.make_fake_platform()
                    else:
                        new_plat = self.platform_factory.make_platform()
                    platform_row += [new_plat]

            self.platforms += [platform_row]
            len_p += 1
        self.len_p = len_p

    def update_model_tree(self, row_min=0, row_max=None):
        if not row_max or row_max > self.len_p:
            row_max = self.len_p

        if row_min < 0:
            row_min = 0

        self.model.children = []

        for i in range(row_min, row_max):
            row = self.platforms[i]
            self.model.children += [p.model for p in row]

    def position_platforms(self, presence):
        for i in range(1,self.len_p):
            k = 0
            for j in range(self.n_plats):  # lenght of a row
                if presence[i-1][j]:
                    if j%2 == 0:
                        y_pos = self.y_positions[0]
                    else:
                        y_pos = self.y_positions[1]
                    self.platforms[i][k].set_init_pos(self.x_positions[j], y_pos, -1 + self.z_sep * i)
                    self.platforms[i][k].update_translate_matrix()
                    k += 1

    def get_platforms(self):
        return [p for row in self.platforms for p in row]

    def maximum_height(self):
        return (self.len_p-1)*self.z_sep

    def draw(self, pipeline):
        for row in self.platforms:
            for p in row:
                p.draw(pipeline)