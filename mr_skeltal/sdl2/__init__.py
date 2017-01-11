from ctypes import c_int, c_uint32, POINTER, byref
from enum import IntEnum
from .dll import SDL
from . import window, renderer, event, gl, rect, pixels, texture  # noqa
from .pixels import PixelFormat  # noqa
from .texture import TextureAccess  # noqa
from .event import EventType  # noqa
from .window import (  # noqa
    WindowFlags, WindowPos,
    create_window, destroy_window
)
from .renderer import RendererFlags  # noqa


_CreateWindowAndRenderer = SDL.SDL_CreateWindowAndRenderer
init = SDL.SDL_Init
quit = SDL.SDL_Quit


class Init(IntEnum):
    TIMER          = 0x00000001
    AUDIO          = 0x00000010
    VIDEO          = 0x00000020
    JOYSTICK       = 0x00000200
    HAPTIC         = 0x00001000
    GAMECONTROLLER = 0x00002000
    EVENTS         = 0x00004000
    NOPARACHUTE    = 0x00100000
    EVERYTHING     = (
        TIMER | AUDIO | VIDEO | EVENTS | JOYSTICK | HAPTIC | GAMECONTROLLER
    )


def create_window_and_renderer(size, flags):
    w, r = window.Window(), renderer.Renderer()
    width, height = size

    if _CreateWindowAndRenderer(width, height, flags, byref(w), byref(r)) != 0:
        raise Exception('SDL_CreateWindowAndRenderer() failed!')

    return w, r


_CreateWindowAndRenderer.argtypes = (
    c_int, c_int,
    c_uint32,
    POINTER(window.Window), POINTER(renderer.Renderer)
)
_CreateWindowAndRenderer.restype = c_int
