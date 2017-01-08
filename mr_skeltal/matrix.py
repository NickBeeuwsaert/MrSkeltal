# flake8: noqa: E201
import numpy as np
import math

from math import cos, sin


def rotate_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)

    return np.array([
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1]
    ])


def rotate_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)

    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1]
    ], dtype=np.float32)


def rotate_z(angle):
    c = math.cos(angle)
    s = math.sin(angle)

    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ], dtype=np.float32)


def rotation(rotation):
    x, y, z = rotation
    sx, cx = sin(x), cos(x)
    sy, cy = sin(y), cos(y)
    sz, cz = sin(z), cos(z)

    return np.array([
        [cy * cz, sx * sy * cz - sz * cx,  sx * sz + sy * cx * cz, 0],
        [sz * cy, sx * sy * sz + cx * cz, -sx * cz + sy * sz * cx, 0],
        [    -sy,                sx * cy,                 cx * cy, 0],
        [      0,                      0,                       0, 1]
    ], dtype=np.float32)


def translate(translation):
    x, y, z = translation
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def scale(scale):
    x, y, z = scale
    return np.array([
        [x, 0, 0, 0],
        [0, y, 0, 0],
        [0, 0, z, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def unit(vec):
    return np.divide(vec, np.linalg.norm(vec), dtype=np.float32)


def look_at(eye, center, up):
    f = unit(np.subtract(center, eye))

    up_prime = unit(up)

    s = np.cross(f, up_prime)
    u = np.cross(unit(s), f)

    mat = np.identity(4, dtype=np.float32)
    mat[:3, :3] = np.stack([s, u, -f], axis=0)

    mat = np.dot(mat, translate(np.negative(eye)))

    return mat


def perspective(fov_y, aspect, z_near, z_far):
    f = 1 / math.tan(fov_y / 2)

    return np.array([
        [f / aspect, 0,                                   0,                                       0],
        [         0, f,                                   0,                                       0],
        [         0, 0, (z_near + z_far) / (z_near - z_far), (2 * z_near * z_far) / (z_near - z_far)],
        [         0, 0,                                  -1,                                       0]
    ], dtype=np.float32)


def ortho(left, right, bottom, top, near, far):
    tx = -(right + left) / (right - left)
    ty = -(top + bottom) / (top - bottom)
    tz = -(far + near) / (far - near)

    return np.array([
        [2 / (right - left), 0, 0, tx],
        [0, 2 / (top - bottom), 0, ty],
        [0, 0, 2 / (far - near), tz],
        [0, 0, 0, 1]
    ], dtype=np.float32)
