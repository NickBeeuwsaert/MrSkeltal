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
import pygame
import numpy as np

from . import matrix
from .ms3d import MS3DModel
from .bone_model import BoneModel

Vector = namedtuple('Vector', 'x y z')
UP = [0, 1, 0]

parser = argparse.ArgumentParser()
parser.add_argument('model', metavar='MODEL.MS3D', type=str)
parser.add_argument('--show-skeleton', action='store_true')

args = parser.parse_args()

pygame.init()
pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)

glViewport(0, 0, 800, 600)

glEnable(GL_DEPTH_TEST)
glClearColor(0, 0, 0, 0)

model = MS3DModel(args.model)
bone_model = BoneModel()
start = time.time()

projection_matrix = matrix.perspective(math.radians(45), 800 / 600, 0.1, 1000)

# Fit the model into the viewport
min_vert, max_vert = map(Vector._make, model.bbox)
model_h = max_vert.y - min_vert.y
model_w = max_vert.x - min_vert.x

distance = max(model_h, model_w) / (2 * math.tan(math.radians(45 / 2)))
distance = distance + max_vert.z

view_matrix = matrix.look_at(
    eye=(0, model_h / 2, -distance),
    center=(0, model_h / 2, 0),
    up=UP
)

rot = matrix.rotate_y(math.radians(1))


def draw_skeleton(model, bone_model):
    for bone in model.bones.values():

        # Don't draw bones that don't have a parent (a root bone)
        # or bones that are connected to a root bone
        if not bone.parent_bone:
            continue
        # if not bone.parent_bone.parent_bone: continue

        # Calculate the difference between this bone and its parent bone
        A = (bone.matrix_at_t(model.timestamp) @ [0, 0, 0, 1])[:3]
        B = (bone.parent_bone.matrix_at_t(model.timestamp) @ [0, 0, 0, 1])[:3]
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
        bone_model.matrix = reduce(np.dot, [
            matrix.translate(B),
            matrix.scale((scale, scale, scale)),
            matrix.axis_angle_rotation(angle, axis)
        ])
        bone_model.render(view_matrix, projection_matrix)


running = True
while running:
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Update the timestamp for the models animation
    model.timestamp = time.time() - start
    model.render(view_matrix, projection_matrix)

    # Draw the models skeleton
    if args.show_skeleton:
        glClear(GL_DEPTH_BUFFER_BIT)
        draw_skeleton(model, bone_model)

    # rotate the view by one degree
    view_matrix = view_matrix @ rot
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
