from collections import namedtuple
import math

from OpenGL.GL import *  # noqa: F403
import pygame

from . import matrix
from .ms3d import MS3DModel
import time

Vector = namedtuple('Vector', 'x y z')

pygame.init()
pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL)

glViewport(0, 0, 800, 600)

glEnable(GL_DEPTH_TEST)
glClearColor(0, 0, 0, 0)

# model = MS3DModel('harry_potter.ms3d')
model = MS3DModel('guy_anim.ms3d')
start = time.time()

projection_matrix = matrix.perspective(math.radians(45), 800 / 600, 0.1, 100)

# Fit the model into the viewport
min_vert, max_vert = map(Vector._make, model.bbox)
model_h = max_vert.y - min_vert.y
model_w = max_vert.x - min_vert.x

distance = max(model_h, model_w) / (2 * math.tan(math.radians(45 / 2)))
distance = distance + max_vert.z

view_matrix = matrix.look_at(
    eye=(0, model_h / 2, -distance),
    center=(0, model_h / 2, 0),
    up=(0, 1, 0)
)

rot = matrix.rotate_y(math.radians(1))
view_matrix = view_matrix @ matrix.rotate_y(math.radians(180))

running = True
while running:
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    model.timestamp = time.time() - start
    model.render(view_matrix, projection_matrix)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
