import argparse
from collections import namedtuple
from functools import reduce
import math
import time

from OpenGL.GL import (
    glViewport, glClear, glEnable, glClearColor
)
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST
)
import numpy as np

from . import matrix
from . import sdl2
from .ms3d import MS3DModel
from .bone_model import BoneModel

Vector = namedtuple('Vector', 'x y z')
UP = [0, 1, 0]


def lerp(a, b, t):
    return np.add(a, np.multiply(np.subtract(b, a), t))


def model_skeleton_matrices(model):
    for bone in model.bones.values():
        # Skip bones that don't have a parent bone
        if not bone.parent_bone:
            continue

        # Calculate the difference between this bone and its parent bone
        A = np.dot(
            bone.matrix_at_t(model.timestamp), [0, 0, 0, 1]
        )[:3]
        B = np.dot(
            bone.parent_bone.matrix_at_t(model.timestamp), [0, 0, 0, 1]
        )[:3]
        delta = A - B
        scale = np.linalg.norm(delta)

        # Don't attempt to draw bones that are so small they cause a zero
        # division error
        if np.isclose(scale, 0.0):
            continue

        angle = math.acos(np.dot(UP, delta / scale))
        # Get the vector that is perpendicular to the plain formed by the UP
        # vector And the current orientation of the bone
        axis = np.cross(UP, delta)

        # Translate, scale and rotate the bone
        yield reduce(np.dot, [
            matrix.translate(B),
            matrix.scale((scale, scale, scale)),
            matrix.axis_angle_rotation(angle, axis)
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model', metavar='MODEL.MS3D', type=str)
    parser.add_argument('--show-skeleton', action='store_true')

    args = parser.parse_args()

    sdl2.init()
    window = sdl2.create_window(
        'Vertex Skinning',
        (
            sdl2.WindowPos.UNDEFINED,
            sdl2.WindowPos.UNDEFINED,
            800, 600
        ),
        sdl2.WindowFlags.OPENGL
    )
    gl_context = sdl2.gl.create_context(window)

    glViewport(0, 0, 800, 600)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0, 0)

    model = MS3DModel(args.model)
    bone_model = BoneModel()
    start = time.time()

    projection_matrix = matrix.perspective(
        math.radians(45),
        800 / 600, 0.1,
        1000
    )

    # Fit the model into the viewport
    min_vert, max_vert = map(Vector._make, model.bbox)
    model_h = max_vert.y - min_vert.y
    model_w = max_vert.x - min_vert.x

    model_center = lerp(min_vert, max_vert, 1 / 2)

    distance = max(model_h, model_w) / (2 * math.tan(math.radians(45 / 2)))
    distance = distance + max_vert.z

    view_matrix = matrix.look_at(
        eye=np.subtract(model_center, [0, 0, distance]),
        center=model_center,
        up=UP
    )

    rot = matrix.rotate_y(math.radians(1))

    running = True
    while running:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Update models current animation frame
        model.timestamp = time.time() - start
        # Draw the model
        model.render(view_matrix, projection_matrix)

        if args.show_skeleton:
            glClear(GL_DEPTH_BUFFER_BIT)
            for M in model_skeleton_matrices(model):
                bone_model.matrix = M
                bone_model.render(view_matrix, projection_matrix)

        # Rotate the view by 1 degree
        view_matrix = np.dot(view_matrix, rot)

        sdl2.gl.swap_window(window)
        for event in sdl2.event.poll():
            if event.type == sdl2.EventType.QUIT:
                running = False

    sdl2.gl.delete_context(gl_context)
    sdl2.window.destroy_window(window)


if __name__ == '__main__':
    main()
