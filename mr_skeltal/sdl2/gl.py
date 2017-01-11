from ctypes import c_void_p

from . import SDL
from .window import Window


class GLContext(c_void_p):
    pass


_GL_CreateContext = SDL.SDL_GL_CreateContext
delete_context = SDL.SDL_GL_DeleteContext
swap_window = SDL.SDL_GL_SwapWindow


def create_context(window):
    context = _GL_CreateContext(window)

    if context is None:
        raise Exception('Error creating GL Context!')

    return context


delete_context.argtypes = (GLContext, )
swap_window.argtypes = (Window, )
_GL_CreateContext.argtypes = (Window, )
_GL_CreateContext.restype = GLContext
