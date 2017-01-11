from ctypes import c_void_p, c_int, c_uint32, c_uint8, POINTER, byref
from enum import IntEnum

from . import SDL
from .rect import Rect
from .texture import Texture
from .window import Window


class RendererFlags(IntEnum):
    SOFTWARE      = 1 << 0
    ACCELERATED   = 1 << 1
    PRESENTVSYNC  = 1 << 2
    TARGETTEXTURE = 1 << 3


_SetRenderDrawColor = SDL.SDL_SetRenderDrawColor
_GetRenderDrawColor = SDL.SDL_GetRenderDrawColor
_SetRenderTarget = SDL.SDL_SetRenderTarget
_GetRenderTarget = SDL.SDL_GetRenderTarget
render_draw_rect = SDL.SDL_RenderDrawRect
render_fill_rect = SDL.SDL_RenderFillRect
render_present = SDL.SDL_RenderPresent
destroy_renderer = SDL.SDL_DestroyRenderer
_CreateRenderer = SDL.SDL_CreateRenderer
_RenderCopy = SDL.SDL_RenderCopy
render_clear = SDL.SDL_RenderClear


def create_renderer(window: Window, index: int=-1, flags: RendererFlags=0):
    return _CreateRenderer(window, index, flags)


def set_render_draw_color(renderer, color):
    r, g, b, a = color

    _SetRenderDrawColor(renderer, r, g, b, a)


def get_render_draw_color(renderer):
    r, g, b, a = c_uint8(), c_uint8(), c_uint8(), c_uint8()

    _GetRenderDrawColor(renderer, byref(r), byref(g), byref(b), byref(a))

    return r, g, b, a


class Renderer(c_void_p):
    draw_color = property(get_render_draw_color, set_render_draw_color)

    def draw_rect(self, rect):
        return render_draw_rect(self, rect)

    def fill_rect(self, rect):
        return render_fill_rect(self, rect)

    def present(self):
        render_present(self)

    def clear(self):
        render_clear(self)

    def copy(self, texture, srcrect, dstrect):
        _RenderCopy(self, texture, srcrect, dstrect)

    target = property(_GetRenderTarget, _SetRenderTarget)


_SetRenderDrawColor.argtypes = (Renderer, c_uint8, c_uint8, c_uint8, c_uint8)
_GetRenderDrawColor.argtypes = (
    c_void_p,
    POINTER(c_uint8), POINTER(c_uint8), POINTER(c_uint8), POINTER(c_uint8)
)
_SetRenderTarget.argtypes = (Renderer, Texture)
_GetRenderTarget.argtypes = (Renderer, )
_GetRenderTarget.restype = Texture
render_draw_rect.argtypes = (Renderer, POINTER(Rect))
render_fill_rect.argtypes = (Renderer, POINTER(Rect))
render_present.argtypes = (Renderer, )
destroy_renderer.argtypes = (Renderer, )
_CreateRenderer.argtypes = (Window, c_int, c_uint32)
_CreateRenderer.restype = Renderer
_RenderCopy.argtypes = (Renderer, Texture, POINTER(Rect), POINTER(Rect))
render_clear.argtypes = (Renderer, )
