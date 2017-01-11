from textwrap import dedent

import numpy as np
from OpenGL.GL import *

from .shader import Uniform, Attribute, Shader
from .decorator import reify


class SimpleShader(Shader):
    vertex_shader = dedent("""\
        #version 120
        uniform mat4 uMVMatrix;
        uniform mat4 uPMatrix;

        attribute vec4 aVertex;

        void main(void) {
            gl_Position = uPMatrix * uMVMatrix * aVertex;
        }""")

    fragment_shader = dedent("""\
        uniform float uColor;

        void main() {
            gl_FragColor = vec4(uColor);
        }""")

    model_view_matrix = Uniform('uMVMatrix')
    projection_matrix = Uniform('uPMatrix')
    color_uniform = Uniform('uColor')

    vertices = Attribute('aVertex')

    def render(self, model, view_matrix, projection_matrix):
        glUseProgram(self.program)

        glEnableVertexAttribArray(self.vertices)

        glUniformMatrix4fv(self.model_view_matrix, 1, GL_TRUE, view_matrix @ model.matrix)
        glUniformMatrix4fv(self.projection_matrix, 1, GL_TRUE, projection_matrix)

        glVertexAttribPointer(self.vertices, 3, GL_FLOAT, GL_FALSE, 0, model.vertex_buffer)

        glUniform1f(self.color_uniform, 0)
        glDrawElements(GL_LINES, model.line_buffer.size, GL_UNSIGNED_BYTE, model.line_buffer)

        glUniform1f(self.color_uniform, 0.5)
        glDrawElements(GL_TRIANGLES, model.index_buffer.size, GL_UNSIGNED_BYTE, model.index_buffer)

        glDisableVertexAttribArray(self.vertices)


class BoneModel(object):
    def __init__(self):
        self.shader = SimpleShader()

    @reify
    def vertex_buffer(self):
        return np.array([
            [0, 0, 0],
            [-0.1, 0.1, 0.1], # left front
            [ 0.1, 0.1, 0.1], # right front
            [-0.1, 0.1,-0.1], # left back
            [ 0.1, 0.1,-0.1], # right back
            [0, 1, 0]
        ], dtype=np.float32)

    @reify
    def index_buffer(self):
        return np.array([
            [0, 1, 2], [0, 2, 4], [0, 4, 3], [0, 3, 1],
            [5, 1, 2], [5, 2, 4], [5, 4, 3], [5, 3, 1],
        ], dtype=np.uint8)

    @reify
    def line_buffer(self):
        return np.array([
            [1, 2], [2, 4], [4, 3], [3, 1],
            [0, 1], [0, 2], [0, 3], [0, 4],
            [5, 1], [5, 2], [5, 3], [5, 4],
        ], dtype=np.uint8)

    @reify
    def matrix(self):
        return np.identity(4, dtype=np.float32)

    def render(self, view_matrix, projection_matrix):
        self.shader.render(self, view_matrix, projection_matrix)
