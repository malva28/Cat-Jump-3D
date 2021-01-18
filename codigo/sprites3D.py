"""
autor: Valentina Garrido
"""

import matplotlib.image as mpimg

import basic_shapes as bs

from abc import ABC,abstractmethod

import numpy as np


images = []
folder = './textures/'


class Traversal(ABC):
    def __init__(self, np_array):
        dim = np_array.shape
        self.rows = dim[0]
        self.columns = dim[1]
        self.array = np_array

    def __iter__(self):
        self.i = 0
        self.j = 0
        return self

    @abstractmethod
    def __next__(self):
        pass


class HorizontalTraversal(Traversal):
    def __init__(self, np_array):
        super().__init__(np_array)

    def __next__(self):
        if self.i < self.rows:
            item = self.array[self.i][self.j]
            ind = (self.i, self.j)

            if self.j == 0:
                jump = (self.i-1, self.columns)
            else:
                jump = False

            self.j += 1
            if self.j >= self.columns:
                self.j = 0
                self.i +=1
            return [item, ind, jump]
        else:
            raise StopIteration


class VerticalTraversal(Traversal):
    def __init__(self, np_array):
        super().__init__(np_array)

    def __next__(self):
        if self.j < self.columns:
            item = self.array[self.i][self.j]
            ind = (self.i, self.j)
            if self.i == 0:
                jump = (self.rows, self.j - 1)
            else:
                jump = False

            self.i += 1

            if self.i >= self.rows:
                self.i = 0
                self.j +=1
            return [item, ind, jump]
        else:
            raise StopIteration

def divideImageByOpacity(np_img, traversal = HorizontalTraversal ,opacity_tolerance = 0.2):
    t = iter(traversal(np_img))
    strips = []
    foundSolidPixel = False
    i = 0
    while True:
        try:
            res = next(t)
            pixel = res[0]
            ind = res[1]
            jump = res[2]
            if foundSolidPixel and jump:
                foundSolidPixel = False
                strip.append(jump)
                strips.append(strip)
            opacity = pixel[3]
            i += 1
            if opacity > opacity_tolerance:
                if foundSolidPixel:
                    continue
                else:
                    foundSolidPixel = True
                    strip = [ind]
            else:
                if not foundSolidPixel:
                    continue
                else:
                    foundSolidPixel = False
                    strip.append(ind)
                    strips.append(strip)

        except StopIteration:
            break
    return strips


def create_3D_sprite_single_color(filename, color={'r':0., 'g':0., 'b': 0.}, depth = 0.5):
    np_img = mpimg.imread(filename)

    rows = np_img.shape[0]
    cols = np_img.shape[1]

    hstrips = divideImageByOpacity(np_img, traversal=HorizontalTraversal,opacity_tolerance=0.2)
    vstrips = divideImageByOpacity(np_img, traversal=VerticalTraversal, opacity_tolerance=0.2)

    dsize = 1/(max(rows, cols))
    x0 = -dsize*rows/2
    z0 = -dsize*cols/2
    y0 = -depth/2

    start_index = 0
    vertices = []
    indices = []

    for hstrip in hstrips:
        #tapa frontal
        x = x0 + dsize*hstrip[0][0]
        z1 = z0 + dsize*hstrip[0][1]
        z2 = z0 + dsize * hstrip[1][1]

        a = [x,y0+depth, z1]
        b = [x,y0+depth, z2]
        c = [x+dsize,y0+depth,z2]
        d = [x+dsize, y0 + depth,z1]

        _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, b, c, d, color)
        vertices += _vertex
        indices += _indices
        start_index += 4

        #shape = bs_ext.create4VertexColor(a, b, c, d, color['r'], color['g'], color['b'])
        #sprite_shape.append(es.toGPUShape(shape))

        #tapa posterior
        a = [x, y0, z1]
        b = [x, y0, z2]
        c = [x + dsize, y0, z2]
        d = [x + dsize, y0, z1]

        _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, b, c, d, color)
        vertices += _vertex
        indices += _indices
        start_index += 4

        #costado izquierdo
        a = [x, y0, z1]
        b = [x+dsize, y0, z1]
        c = [x + dsize, y0+depth, z1]
        d = [x, y0 + depth, z1]

        _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, b, c, d, color)
        vertices += _vertex
        indices += _indices
        start_index += 4

        #costado derecho
        a = [x, y0, z2]
        b = [x + dsize, y0, z2]
        c = [x + dsize, y0 + depth, z2]
        d = [x, y0 + depth, z2]

        _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, b, c, d, color)
        vertices += _vertex
        indices += _indices
        start_index += 4

    for vstrip in vstrips:
        z = z0 + dsize * vstrip[0][1]
        x1 = x0 + dsize * vstrip[0][0]
        x2 = x0 + dsize * vstrip[1][0]

        #tapa de arriba
        a = [x1, y0, z]
        b = [x1, y0+depth, z]
        c = [x1, y0 + depth, z+dsize]
        d = [x1, y0, z + dsize]

        _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, b, c, d, color)
        vertices += _vertex
        indices += _indices
        start_index += 4

        #tapa de abajo
        a = [x2, y0, z]
        b = [x2, y0 + depth, z]
        c = [x2, y0 + depth, z + dsize]
        d = [x2, y0, z + dsize]

        _vertex, _indices = createColorNormalsQuadIndexation(start_index, a, b, c, d, color)
        vertices += _vertex
        indices += _indices
        start_index += 4

    return bs.Shape(vertices, indices)


def createColorNormalsQuadIndexation(start_index, a, b, c, d, color):
    # Computing normal from a b c
    v1 = np.array([a[i] - b[i] for i in range(3)])
    v2 = np.array([b[i] - c[i] for i in range(3)])
    v1xv2 = np.cross(v1, v2)

    # Defining locations and colors for each vertex of the shape
    vertices = [
        #        positions               colors                 normals
        a[0], a[1], a[2], color['r'], color['g'], color['b'], v1xv2[0], v1xv2[1], v1xv2[2],
        b[0], b[1], b[2], color['r'], color['g'], color['b'], v1xv2[0], v1xv2[1], v1xv2[2],
        c[0], c[1], c[2], color['r'], color['g'], color['b'], v1xv2[0], v1xv2[1], v1xv2[2],
        d[0], d[1], d[2], color['r'], color['g'], color['b'], v1xv2[0], v1xv2[1], v1xv2[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        start_index, start_index + 1, start_index + 2,
                     start_index + 2, start_index + 3, start_index
    ]

    return vertices, indices
