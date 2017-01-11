from math import radians, sqrt
import itertools

import numpy as np

from mr_skeltal import matrix

def test_rotate_x():
    np.testing.assert_almost_equal(
        matrix.rotate_x(radians(90)),
        np.array([
            [1, 0,  0, 0],
            [0, 0, -1, 0],
            [0, 1,  0, 0],
            [0, 0,  0, 1]
        ])
    )

    np.testing.assert_almost_equal(
        matrix.rotate_x(radians(45)),
        np.array([
            [1,         0,          0, 0],
            [0, 1/sqrt(2), -1/sqrt(2), 0],
            [0, 1/sqrt(2),  1/sqrt(2), 0],
            [0,         0,          0, 1]
        ])
    )

    for angle in (15, 30, 45, 60, 75, 90):
        np.testing.assert_approx_equal(
            np.linalg.det(matrix.rotate_x(radians(angle))),
            1.0
        )

def test_rotate_y():
    np.testing.assert_almost_equal(
        matrix.rotate_y(radians(90)),
        np.array([
            [ 0, 0, 1, 0],
            [ 0, 1, 0, 0],
            [-1, 0, 0, 0],
            [ 0, 0, 0, 1]
        ])
    )

    np.testing.assert_almost_equal(
        matrix.rotate_y(radians(45)),
        np.array([
            [ 1/sqrt(2), 0, 1/sqrt(2), 0],
            [         0, 1,         0, 0],
            [-1/sqrt(2), 0, 1/sqrt(2), 0],
            [         0, 0,         0, 1]
        ])
    )
    for angle in (15, 30, 45, 60, 75, 90):
        np.testing.assert_approx_equal(
            np.linalg.det(matrix.rotate_y(radians(angle))),
            1.0
        )

def test_rotate_z():
    np.testing.assert_almost_equal(
        matrix.rotate_z(radians(90)),
        np.array([
            [0, -1, 0, 0],
            [1,  0, 0, 0],
            [0,  0, 1, 0],
            [0,  0, 0, 1]
        ])
    )

    np.testing.assert_almost_equal(
        matrix.rotate_z(radians(45)),
        np.array([
            [1/sqrt(2), -1/sqrt(2), 0, 0],
            [1/sqrt(2),  1/sqrt(2), 0, 0],
            [        0,          0, 1, 0],
            [        0,          0, 0, 1]
        ])
    )

    for angle in (15, 30, 45, 60, 75, 90):
        np.testing.assert_approx_equal(
            np.linalg.det(matrix.rotate_z(radians(angle))),
            1.0
        )

def test_rotation():
    np.testing.assert_almost_equal(
        matrix.rotation((radians(90), radians(90), radians(90))),
        np.array([
            [ 0, 0, 1, 0],
            [ 0, 1, 0, 0],
            [-1, 0, 0, 0],
            [ 0, 0, 0, 1]
        ])
    )

    for x, y, z in itertools.product([15, 30, 45, 60, 75, 90], repeat=3):
        np.testing.assert_approx_equal(
            np.linalg.det(matrix.rotation((
                radians(x),
                radians(y),
                radians(z)
            ))),
            1.0
        )
