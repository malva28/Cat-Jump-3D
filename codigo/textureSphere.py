"""
autor: Valentina Garrido
autor: Alonso Utreras
"""

from PIL import Image
import numpy as np
import basic_shapes as bs


def _generatorSphereTextureNormals(filename, nTheta, nPhi, min_theta=0, max_theta=np.pi, vertices=[], indices=[], start_index=0, texture_method = None):
    image = Image.open(filename)
    img_data = np.array(list(image.getdata()), np.uint8)

    theta_angs = np.linspace(min_theta, max_theta, nTheta, endpoint=True)
    phi_angs = np.linspace(0, 2 * np.pi, nPhi, endpoint=True)

    n_theta = len(theta_angs)
    n_phi = len(phi_angs)

    r = 0.5

    for theta_ind in range(n_theta - 1):  # vertical
        cos_theta = np.cos(theta_angs[theta_ind])  # z_top
        cos_theta_next = np.cos(theta_angs[theta_ind + 1])  # z_bottom

        sin_theta = np.sin(theta_angs[theta_ind])
        sin_theta_next = np.sin(theta_angs[theta_ind + 1])

        # d === c <---- z_top
        # |     |
        # |     |
        # a === b  <--- z_bottom
        # ^     ^
        # phi   phi + dphi
        for phi_ind in range(n_phi - 1):  # horizontal
            cos_phi = np.cos(phi_angs[phi_ind])
            cos_phi_next = np.cos(phi_angs[phi_ind + 1])
            sin_phi = np.sin(phi_angs[phi_ind])
            sin_phi_next = np.sin(phi_angs[phi_ind + 1])
            # we will asume radius = 1, so scaling should be enough.
            # x = cosφ sinθ
            # y = sinφ sinθ
            # z = cosθ

            ind_args = [theta_ind, n_theta, phi_ind, n_phi]
            tri_args = [cos_phi, cos_phi_next, sin_phi, sin_phi_next, sin_theta, sin_theta_next]

            n1, n2, n3, n4 = texture_method(ind_args, tri_args)

            #                     X                             Y                          Z
            a = r * np.array([cos_phi * sin_theta_next, sin_phi * sin_theta_next, cos_theta_next])
            b = r * np.array([cos_phi_next * sin_theta_next, sin_phi_next * sin_theta_next, cos_theta_next])
            c = r * np.array([cos_phi_next * sin_theta, sin_phi_next * sin_theta, cos_theta])
            d = r * np.array([cos_phi * sin_theta, sin_phi * sin_theta, cos_theta])

            a_n = 2 * np.array([cos_phi * sin_theta_next, sin_phi * sin_theta_next, cos_theta_next])
            b_n = 2 * np.array([cos_phi_next * sin_theta_next, sin_phi_next * sin_theta_next, cos_theta_next])
            c_n = 2 * np.array([cos_phi_next * sin_theta, sin_phi_next * sin_theta, cos_theta])
            d_n = 2 * np.array([cos_phi * sin_theta, sin_phi * sin_theta, cos_theta])

            mu = 0.5
            sigma = 0.1
            color = np.random.normal(mu, sigma, 3)
            _vertex, _indices, _filename = createColorSpecificTextureNormals(filename, start_index, a, b, c, d,
                                                                                   a_n, b_n, c_n, d_n, n1, n2, n3, n4)

            vertices += _vertex
            indices += _indices
            start_index += 4

    return start_index


def generateSphereTextureNormals(filename, nTheta, nPhi):
    vertices = []
    indices = []

    _generatorSphereTextureNormals(filename, nTheta, nPhi, vertices, indices, texture_method=texture_to_sphere)
    return bs.Shape(vertices, indices, filename)


def generateSemiSphereTextureNormals(filename, nTheta, nPhi):
    vertices = []
    indices = []

    start_index = _generatorSphereTextureNormals(filename, nTheta, nPhi, min_theta= 0, max_theta= np.pi/2,
                                                 vertices=vertices,indices=indices, texture_method=texture_to_semisphere)
    _generatorSphereTextureNormals(filename, nTheta, nPhi, min_theta=np.pi/2, max_theta=np.pi,
                                                 vertices=vertices,
                                                 indices=indices, texture_method=texture_to_semisphere, start_index=start_index)
    return bs.Shape(vertices, indices, filename)

def texture_to_sphere(ind_args, tri_args):
    theta_ind, n_theta, phi_ind, n_phi = ind_args

    # Assign texture coordinates
    u = theta_ind / n_theta
    v = phi_ind / n_phi

    next_u = (theta_ind + 1) / n_theta
    next_v = (phi_ind + 1) / n_phi

    n1 = (next_u, v)
    n2 = (next_u, next_v)
    n3 = (u, next_v)
    n4 = (u, v)

    return n1, n2, n3, n4


def texture_to_semisphere(ind_args, tri_args):
    cos_phi, cos_phi_next, sin_phi, sin_phi_next, sin_theta, sin_theta_next = tri_args

    # change range to [-0.5, 0.5] and then shift by 0.5 so it lies in range [0,1]
    n1 = [cos_phi * sin_theta_next * 0.5 + 0.5, sin_phi * sin_theta_next * 0.5 + 0.5]
    n2 = [cos_phi_next * sin_theta_next * 0.5 + 0.5, sin_phi_next * sin_theta_next * 0.5 + 0.5]
    n3 = [cos_phi_next * sin_theta * 0.5 + 0.5, sin_phi_next * sin_theta * 0.5 + 0.5]
    n4 = [cos_phi * sin_theta * 0.5 + 0.5, sin_phi * sin_theta * 0.5 + 0.5]

    return n1, n2, n3, n4


def createColorSpecificTextureNormals(filename, start_index, a, b, c, d, a_n, b_n, c_n, d_n, n1=(0,0), n2=(1,0), n3=(1,1), n4=(0,1)):

    # Dissemble texture coordinates
    tx1, ty1 = n1
    tx2, ty2 = n2
    tx3, ty3 = n3
    tx4, ty4 = n4

    # Defining locations and colors for each vertex of the shape
    vertices = [
        #    positions    textures       normals
        a[0], a[1], a[2], tx1, ty1, a_n[0], a_n[1], a_n[2],
        b[0], b[1], b[2], tx2, ty2, b_n[0], b_n[1], b_n[2],
        c[0], c[1], c[2], tx3, ty3, c_n[0], c_n[1], c_n[2],
        d[0], d[1], d[2], tx4, ty4, d_n[0], d_n[1], d_n[2]
    ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        start_index, start_index + 1, start_index + 2,
                     start_index + 2, start_index + 3, start_index
    ]

    return (vertices, indices, filename)


