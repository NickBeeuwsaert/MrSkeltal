import weakref

from OpenGL.GL import (
    glCreateShader, glCreateProgram,
    glShaderSource, glCompileShader,
    glLinkProgram,
    glGetShaderiv, glGetProgramiv,
    glGetShaderInfoLog, glGetProgramInfoLog,
    glAttachShader,
    glDeleteShader, glDeleteProgram,
    glGetUniformLocation, glGetAttribLocation
)
from OpenGL.GL import (
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
    GL_LINK_STATUS, GL_COMPILE_STATUS,
    GL_FALSE
)


class ShaderException(Exception):
    pass


def load_shader(shader_type, source):
    shader = glCreateShader(shader_type)

    if shader == 0:
        raise ShaderException()

    glShaderSource(shader, source)

    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS, None) == GL_FALSE:
        info_log = glGetShaderInfoLog(shader)
        glDeleteShader(shader)

        raise ShaderException(info_log)

    return shader


def compile_shader(vertex_shader_source, fragment_shader_source):
    vertex_shader = load_shader(GL_VERTEX_SHADER, vertex_shader_source)
    fragment_shader = load_shader(GL_FRAGMENT_SHADER, fragment_shader_source)

    program = glCreateProgram()

    if program == 0:
        raise ShaderException()

    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)

    glLinkProgram(program)

    if glGetProgramiv(program, GL_LINK_STATUS, None) == GL_FALSE:
        info_log = glGetProgramInfoLog(program)
        glDeleteProgram(program)
        raise ShaderException(info_log)

    return program


class Uniform(object):
    def __init__(self, name):
        self.name = name
        self._values = weakref.WeakKeyDictionary()

    def __get__(self, inst, owner):
        if inst not in self._values:
            self._values[inst] = glGetUniformLocation(inst.program, self.name)

        return self._values[inst]


class Attribute(object):
    def __init__(self, name):
        self.name = name
        self._values = weakref.WeakKeyDictionary()

    def __get__(self, inst, owner):
        if inst not in self._values:
            self._values[inst] = glGetAttribLocation(inst.program, self.name)

        return self._values[inst]


class Shader(object):
    vertex_shader = None
    fragment_shader = None

    def __init__(self):
        self.program = compile_shader(self.vertex_shader, self.fragment_shader)
