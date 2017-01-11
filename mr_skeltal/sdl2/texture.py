from contextlib import contextmanager
from ctypes import c_void_p, c_uint32, c_int, c_int32
from ctypes import byref
from enum import IntEnum

from . import SDL
from .pixels import PixelFormat


class TextureAccess(IntEnum):
    STATIC = 0
    STREAMING = 1
    TARGET = 2


_LockTexture = SDL.SDL_LockTexture
unlock_texture = SDL.SDL_UnlockTexture
_CreateTexture = SDL.SDL_CreateTexture
destroy_texture = SDL.SDL_DestroyTexture


def lock_texture(texture, rect=None):
    pixels, pitch = c_void_p(), c_int32()

    if _LockTexture(texture, rect, byref(pixels), byref(pitch)) != 0:
        raise Exception('Trouble locking texture!')

    return pixels, pitch


def create_texture(renderer, format: PixelFormat, access, size):
    w, h = size
    texture = _CreateTexture(renderer, format, access, w, h)

    if texture is None:
        raise Exception('CreateTexture() returned NULL')

    return texture


class Texture(c_void_p):
    @contextmanager
    def lock(self, rect=None):
        pixels, pitch = lock_texture(self, rect)

        yield pixels, pitch

        unlock_texture(self)


_LockTexture.argtypes = (c_void_p, c_void_p, c_void_p, c_void_p)
unlock_texture.argtypes = (c_void_p, )
_CreateTexture.argtypes = (c_void_p, c_uint32, c_int, c_int, c_int)
_CreateTexture.restype = Texture
destroy_texture.argtypes = (Texture, )
