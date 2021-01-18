# coding=utf-8
"""
Archivo utilitario creado para la auxiliar 7, permite definir más figuras
con texturas.

@author ppizarror
"""
import copy

from basic_shapes import Shape as _Shape
from collections import namedtuple
from easy_shaders import GPUShape as _GPUShape
from easy_shaders import toGPUShape as _toGPUShape
from mathlib import _normal_3_points as _normal3
from OpenGL.GL import GL_POLYGON as _GL_POLYGON
from OpenGL.GL import GL_TRIANGLES as _GL_TRIANGLES
from OpenGL.GL import GL_TRUE as _GL_TRUE
from OpenGL.GL import glGetUniformLocation as _glGetUniformLocation
from OpenGL.GL import glUniformMatrix4fv as _glUniformMatrix4fv
from OpenGL.GL import glUseProgram as _glUseProgram
import math
import sys
import transformations2 as _tr

from tr_commands import *

Point = namedtuple('Point', ['x', 'y'])
EPSILON = math.sqrt(sys.float_info.epsilon)


def earclip(polygon):
    """
    Simple earclipping algorithm for a given polygon p.
    polygon is expected to be an array of 2-tuples of the cartesian points of the polygon

    For a polygon with n points it will return n-2 triangles.
    The triangles are returned as an array of 3-tuples where each item in the tuple is a 2-tuple of the cartesian point.

    e.g
    >>> polygon = [(0,1), (-1, 0), (0, -1), (1, 0)]
    >>> triangles = earclip(polygon)
    >>> triangles
    [((1, 0), (0, 1), (-1, 0)), ((1, 0), (-1, 0), (0, -1))]

    Implementation Reference:
        - https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
    """
    ear_vertex = []
    triangles = []

    polygon = [Point(*point) for point in polygon]

    if _is_clockwise(polygon):
        polygon.reverse()

    point_count = len(polygon)
    for i in range(point_count):
        prev_index = i - 1
        prev_point = polygon[prev_index]
        point = polygon[i]
        next_index = (i + 1) % point_count
        next_point = polygon[next_index]

        if _is_ear(prev_point, point, next_point, polygon):
            ear_vertex.append(point)

    while ear_vertex and point_count >= 3:
        ear = ear_vertex.pop(0)
        i = polygon.index(ear)
        prev_index = i - 1
        prev_point = polygon[prev_index]
        next_index = (i + 1) % point_count
        next_point = polygon[next_index]

        polygon.remove(ear)
        point_count -= 1
        triangles.append(((prev_point.x, prev_point.y), (ear.x, ear.y), (next_point.x, next_point.y)))
        if point_count > 3:
            prev_prev_point = polygon[prev_index - 1]
            next_next_index = (i + 1) % point_count
            next_next_point = polygon[next_next_index]

            groups = [
                (prev_prev_point, prev_point, next_point, polygon),
                (prev_point, next_point, next_next_point, polygon),
            ]
            for group in groups:
                p = group[1]
                if _is_ear(*group):
                    if p not in ear_vertex:
                        ear_vertex.append(p)
                elif p in ear_vertex:
                    ear_vertex.remove(p)
    return triangles


def _is_clockwise(polygon):
    s = 0
    polygon_count = len(polygon)
    for i in range(polygon_count):
        point = polygon[i]
        point2 = polygon[(i + 1) % polygon_count]
        s += (point2.x - point.x) * (point2.y + point.y)
    return s > 0


def _is_convex(prev, point, next):
    return _triangle_sum(prev.x, prev.y, point.x, point.y, next.x, next.y) < 0


def _is_ear(p1, p2, p3, polygon):
    ear = _contains_no_points(p1, p2, p3, polygon) and \
          _is_convex(p1, p2, p3) and \
          _triangle_area(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y) > 0
    return ear


def _contains_no_points(p1, p2, p3, polygon):
    for pn in polygon:
        if pn in (p1, p2, p3):
            continue
        elif _is_point_inside(pn, p1, p2, p3):
            return False
    return True


def _is_point_inside(p, a, b, c):
    area = _triangle_area(a.x, a.y, b.x, b.y, c.x, c.y)
    area1 = _triangle_area(p.x, p.y, b.x, b.y, c.x, c.y)
    area2 = _triangle_area(p.x, p.y, a.x, a.y, c.x, c.y)
    area3 = _triangle_area(p.x, p.y, a.x, a.y, b.x, b.y)
    areadiff = abs(area - sum([area1, area2, area3])) < EPSILON
    return areadiff


def _triangle_area(x1, y1, x2, y2, x3, y3):
    return abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2.0)


def _triangle_sum(x1, y1, x2, y2, x3, y3):
    return x1 * (y3 - y2) + x2 * (y1 - y3) + x3 * (y2 - y1)


def calculate_total_area(triangles):
    result = []
    for triangle in triangles:
        sides = []
        for i in range(3):
            next_index = (i + 1) % 3
            pt = triangle[i]
            pt2 = triangle[next_index]
            # Distance between two points
            side = math.sqrt(math.pow(pt2[0] - pt[0], 2) + math.pow(pt2[1] - pt[1], 2))
            sides.append(side)
        # Heron's numerically stable forumla for area of a triangle:
        # https://en.wikipedia.org/wiki/Heron%27s_formula
        # However, for line-like triangles of zero area this formula can produce an infinitesimally negative value
        # as an input to sqrt() due to the cumulative arithmetic errors inherent to floating point calculations:
        # https://people.eecs.berkeley.edu/~wkahan/Triangle.pdf
        # For this purpose, abs() is used as a reasonable guard against this condition.
        c, b, a = sorted(sides)
        area = .25 * math.sqrt(abs((a + (b + c)) * (c - (a - b)) * (c + (a - b)) * (a + (b - c))))
        result.append((area, a, b, c))
    triangle_area = sum(tri[0] for tri in result)
    return triangle_area


# Merged shape
class AdvancedGPUShape:
    def __init__(self, shapes, model=_tr.identity(), enabled=True, shader=None):
        """
        Constructor.

        :param shapes: List or GPUShape object
        :param model: Basic model transformation matrix
        :param enabled: Indicates if the shape is enabled or not
        :param shader: Shader program
        """
        if not isinstance(shapes, list):
            shapes = [shapes]
        for i in range(len(shapes)):
            if not isinstance(shapes[i], _GPUShape):
                raise Exception('Object {0} of shapes list is not GPUShape instance'.format(i))

        self._shapes = shapes
        self._model = model
        self._modelPrev = None
        self._enabled = enabled
        self._shader = shader

    def setShader(self, shader):
        """
        Set shader.

        :param shader:
        :return:
        """
        self._shader = shader

    def execute(self, command, *params):
        tr_matrix = command_dictionary[command](*params)
        self._model = _tr.matmul([tr_matrix, self._model])

    def translate(self, tx=0, ty=0, tz=0):
        """
        Translate model.

        :param tx:
        :param ty:
        :param tz:
        :return:
        """
        self.execute(Command.TRANSLATE, tx, ty, tz)

    def scale(self, sx=1, sy=1, sz=1):
        """
        Scale model.

        :param sx:
        :param sy:
        :param sz:
        :return:
        """
        self.execute(Command.SCALE, sx, sy, sz)

    def uniformScale(self, s=1):
        """
        Uniform scale model.

        :param s:
        :return:
        """
        self.execute(Command.UNIFORM_SCALE, s)

    def rotationX(self, theta=0):
        """
        Rotate model.

        :param theta:
        :return:
        """
        self.execute(Command.ROTATION_X, theta)

    def rotationY(self, theta=0):
        """
        Rotate model.

        :param theta:
        :return:
        """
        self.execute(Command.ROTATION_Y, theta)

    def rotationZ(self, theta=0):
        """
        Rotate model.

        :param theta:
        :return:
        """
        self.execute(Command.ROTATION_Z, theta)

    def rotationA(self, theta, axis):
        """
        Rotate model.

        :param theta:
        :param axis:
        :return:
        """
        self.execute(Command.ROTATION_A, theta, axis)

    def shearing(self, xy=0, yx=0, xz=0, zx=0, yz=0, zy=0):
        """
        Apply shear to model.

        :param xy:
        :param yx:
        :param xz:
        :param zx:
        :param yz:
        :param zy:
        :return:
        """
        self.execute(Command.SHEARING, xy, yx, xz, zx, yz, zy)

    def applyTemporalTransform(self, t):
        """
        Apply temporal transform to model until drawing.

        :param t:
        :return:
        """
        self._modelPrev = self._model
        self._model = _tr.matmul([t, self._model])

    def draw(self, view, projection, mode=_GL_TRIANGLES, shader=None, usemodel=True):
        """
        Draw model.

        :param view:
        :param projection:
        :param mode:
        :param shader:
        :param usemodel:
        :return:
        """
        if not self._enabled:
            return
        if mode is None:
            mode = _GL_POLYGON
        if shader is None:
            if self._shader is None:
                raise Exception('MergedShape shader is not set')
            shader = self._shader
        _glUseProgram(shader.shaderProgram)
        if usemodel:
            _glUniformMatrix4fv(_glGetUniformLocation(shader.shaderProgram, 'model'), 1, _GL_TRUE, self._model)
        _glUniformMatrix4fv(_glGetUniformLocation(shader.shaderProgram, 'projection'), 1, _GL_TRUE, projection)
        _glUniformMatrix4fv(_glGetUniformLocation(shader.shaderProgram, 'view'), 1, _GL_TRUE, view)
        for i in self._shapes:
            shader.drawShape(i, mode)
        if self._modelPrev is not None:
            self._model = self._modelPrev
            self._modelPrev = None

    def disable(self):
        """
        Disable the model.

        :return:
        """
        self._enabled = False

    def enable(self):
        """
        Enable the model.

        :return:
        """
        self._enabled = True

    def get_model(self):
        return copy.deepcopy(self._model)

    def clone(self):
        """
        Clone the model.

        :return:
        """
        return AdvancedGPUShape(self._shapes.copy(), self.get_model(), enabled=self._enabled, shader=self._shader)


def __vertexUnpack3(vertex):
    """
    Extend vertex to 3 dimension.

    :param vertex:
    :return:
    """
    if len(vertex) == 2:
        vertex = vertex + (0,)
    return vertex


def createColorPlaneFromCurve(curve, triangulate, r, g, b, center=None):
    """
    Creates a plane from a curve and a center.

    :param curve: Curve vertex list
    :param triangulate: Create plane from curve triangulation
    :param center: Center position
    :param r: Red color
    :param g: Green color
    :param b: Blue color
    :return: Merged shape
    :rtype: AdvancedGPUShape
    """
    shapes = []

    # Use delaunay triangulation
    if triangulate:
        k = []
        for i in curve:
            k.append((i[0], i[1]))
        tri = earclip(k)
        for i in tri:
            x1, y1 = i[0]
            x2, y2 = i[1]
            x3, y3 = i[2]
            shape = createTriangleColor((x1, y1, 0), (x2, y2, 0), (x3, y3, 0), r, g, b)
            shapes.append(_toGPUShape(shape))
    else:
        if center is None:
            center = curve[0]
        for i in range(0, len(curve) - 1):
            x1, y1 = curve[i]
            x2, y2 = curve[(i + 1) % len(curve)]
            c1, c2 = center
            shape = createTriangleColor((x1, y1, 0), (x2, y2, 0), (c1, c2, 0), r, g, b)
            shapes.append(_toGPUShape(shape))
    return AdvancedGPUShape(shapes)


def create4VertexTexture(image_filename, p1, p2, p3, p4, nx=1, ny=1):
    """
    Creates a 4-vertex poly with texture.

    :param image_filename: Image
    :param p1: Vertex (x,y,z)
    :param p2: Vertex (x,y,z)
    :param p3: Vertex (x,y,z)
    :param p4: Vertex (x,y,z)
    :param nx: Texture coord pos
    :param ny: Texture coord pos
    :return:
    """
    # Extend
    p1 = __vertexUnpack3(p1)
    p2 = __vertexUnpack3(p2)
    p3 = __vertexUnpack3(p3)
    p4 = __vertexUnpack3(p4)

    # Dissamble vertices
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3
    x4, y4, z4 = p4

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        x1, y1, z1, 0, 0,
        x2, y2, z2, nx, 0,
        x3, y3, z3, nx, ny,
        x4, y4, z4, 0, ny
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2,
        2, 3, 0]

    return _Shape(vertices, indices, image_filename)


def create4VertexTextureNormal(image_filename, p1, p2, p3, p4, nx=1, ny=1):
    """
    Creates a 4-vertex poly with texture.

    :param image_filename: Image
    :param p1: Vertex (x,y,z)
    :param p2: Vertex (x,y,z)
    :param p3: Vertex (x,y,z)
    :param p4: Vertex (x,y,z)
    :param nx: Texture coord pos
    :param ny: Texture coord pos
    :return:
    """
    # Extend
    p1 = __vertexUnpack3(p1)
    p2 = __vertexUnpack3(p2)
    p3 = __vertexUnpack3(p3)
    p4 = __vertexUnpack3(p4)

    # Dissamble vertices
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3
    x4, y4, z4 = p4

    # Calculate the normal
    normal = _normal3(p3, p2, p1)

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        x1, y1, z1, 0, 0, normal.get_x(), normal.get_y(), normal.get_z(),
        x2, y2, z2, nx, 0, normal.get_x(), normal.get_y(), normal.get_z(),
        x3, y3, z3, nx, ny, normal.get_x(), normal.get_y(), normal.get_z(),
        x4, y4, z4, 0, ny, normal.get_x(), normal.get_y(), normal.get_z()
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2,
        2, 3, 0]

    return _Shape(vertices, indices, image_filename)


def create4VertexColor(p1, p2, p3, p4, r, g, b):
    """
    Creates a 4-vertex poly with color.

    :param p1: Vertex (x,y,z)
    :param p2: Vertex (x,y,z)
    :param p3: Vertex (x,y,z)
    :param p4: Vertex (x,y,z)
    :param r: Red color
    :param g: Green color
    :param b: Blue color
    :return:
    """
    # Extend
    p1 = __vertexUnpack3(p1)
    p2 = __vertexUnpack3(p2)
    p3 = __vertexUnpack3(p3)
    p4 = __vertexUnpack3(p4)

    # Disassemble vertices
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3
    x4, y4, z4 = p4

    # Defining locations and color
    vertices = [
        # X, Y,  Z, R, G, B,
        x1, y1, z1, r, g, b,
        x2, y2, z2, r, g, b,
        x3, y3, z3, r, g, b,
        x4, y4, z4, r, g, b
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2,
        2, 3, 0
    ]

    return _Shape(vertices, indices)


def create4VertexColorNormal(p1, p2, p3, p4, r, g, b):
    """
    Creates a 4-vertex figure with color and normals.

    :param p1: Vertex (x,y,z)
    :param p2: Vertex (x,y,z)
    :param p3: Vertex (x,y,z)
    :param p4: Vertex (x,y,z)
    :param r: Red color
    :param g: Green color
    :param b: Blue color
    :return:
    """
    # Extend
    p1 = __vertexUnpack3(p1)
    p2 = __vertexUnpack3(p2)
    p3 = __vertexUnpack3(p3)
    p4 = __vertexUnpack3(p4)

    # Dissamble vertices
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3
    x4, y4, z4 = p4

    # Calculate the normal
    normal = _normal3(p3, p2, p1)

    # Defining locations and color
    vertices = [
        # X, Y,  Z, R, G, B,
        x1, y1, z1, r, g, b, normal.get_x(), normal.get_y(), normal.get_z(),
        x2, y2, z2, r, g, b, normal.get_x(), normal.get_y(), normal.get_z(),
        x3, y3, z3, r, g, b, normal.get_x(), normal.get_y(), normal.get_z(),
        x4, y4, z4, r, g, b, normal.get_x(), normal.get_y(), normal.get_z()
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2,
        2, 3, 0
    ]

    return _Shape(vertices, indices)


def createTriangleTexture(image_filename, p1, p2, p3, nx=1, ny=1):
    """
    Creates a triangle with textures.

    :param image_filename: Image
    :param p1: Vertex (x,y,z)
    :param p2: Vertex (x,y,z)
    :param p3: Vertex (x,y,z)
    :param nx: Texture coord pos
    :param ny: Texture coord pos
    :return:
    """
    # Dissamble vertices
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        # X, Y,  Z,   U,   V
        x1, y1, z1, (nx + ny) / 2, nx,
        x2, y2, z2, 0.0, 0.0,
        x3, y3, z3, ny, 0.0
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2
    ]

    return _Shape(vertices, indices, image_filename)


def createTriangleTextureNormal(image_filename, p1, p2, p3, nx=1, ny=1):
    """
    Creates a triangle with textures.

    :param image_filename: Image
    :param p1: Vertex (x,y,z)
    :param p2: Vertex (x,y,z)
    :param p3: Vertex (x,y,z)
    :param nx: Texture coord pos
    :param ny: Texture coord pos
    :return:
    """
    # Dissamble vertices
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    # Calculate the normal
    normal = _normal3(p3, p2, p1)

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
        # X, Y,  Z,   U,   V
        x1, y1, z1, (nx + ny) / 2, nx, normal.get_x(), normal.get_y(), normal.get_z(),
        x2, y2, z2, 0.0, 0.0, normal.get_x(), normal.get_y(), normal.get_z(),
        x3, y3, z3, ny, 0.0, normal.get_x(), normal.get_y(), normal.get_z()
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2
    ]

    return _Shape(vertices, indices, image_filename)


def createTriangleColor(p1, p2, p3, r, g, b):
    """
    Creates a triangle with color.

    :param p1: Vertex (x,y,z)
    :param p2: Vertex (x,y,z)
    :param p3: Vertex (x,y,z)
    :param r: Red color
    :param g: Green color
    :param b: Blue color
    :return:
    """
    # Extend
    p1 = __vertexUnpack3(p1)
    p2 = __vertexUnpack3(p2)
    p3 = __vertexUnpack3(p3)

    # Dissamble vertices
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    # Defining locations and color
    vertices = [
        # X, Y,  Z, R, G, B,
        x1, y1, z1, r, g, b,
        x2, y2, z2, r, g, b,
        x3, y3, z3, r, g, b,
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2
    ]

    return _Shape(vertices, indices)


def createTriangleColorNormal(p1, p2, p3, r, g, b):
    """
    Creates a triangle with color.

    :param p1: Vertex (x,y,z)
    :param p2: Vertex (x,y,z)
    :param p3: Vertex (x,y,z)
    :param r: Red color
    :param g: Green color
    :param b: Blue color
    :return:
    """
    # Extend
    p1 = __vertexUnpack3(p1)
    p2 = __vertexUnpack3(p2)
    p3 = __vertexUnpack3(p3)

    # Dissamble vertices
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    # Calculate the normal
    normal = _normal3(p3, p2, p1)

    # Defining locations and color
    vertices = [
        # X, Y,  Z, R, G, B,
        x1, y1, z1, r, g, b, normal.get_x(), normal.get_y(), normal.get_z(),
        x2, y2, z2, r, g, b, normal.get_x(), normal.get_y(), normal.get_z(),
        x3, y3, z3, r, g, b, normal.get_x(), normal.get_y(), normal.get_z()
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2
    ]

    return _Shape(vertices, indices)
