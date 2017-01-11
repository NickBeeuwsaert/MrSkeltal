from ctypes import Structure
from ctypes import c_int32, c_void_p, c_bool
from ctypes import byref
import ctypes

from . import SDL


intersects = SDL.SDL_HasIntersection
_EnclosePoints = SDL.SDL_EnclosePoints


class Point(Structure):
    _fields_ = [
        ('x', c_int32),
        ('y', c_int32)
    ]

    def in_rect(self, rect):
        return all([
            self.x >= rect.x,
            self.x < (rect.x + rect.w),
            self.y >= rect.y,
            self.y < (rect.y + rect.h)
        ])


def empty(rect):
    return rect is None or rect.w <= 0 or rect.h <= 0


def equals(a, b):
    return None not in (a, b) and all([
        a.x == b.x, a.y == b.y,
        a.w == b.w, a.h == b.h
    ])


class Rect(Structure):
    _fields_ = [
        ('x', c_int32),
        ('y', c_int32),
        ('w', c_int32),
        ('h', c_int32),
    ]

    empty = property(empty)
    intersects = intersects
    __eq__ = equals


def enclose(points, clip=None):
    result = Rect()

    arr = (Point * len(points))(*points)
    _EnclosePoints(arr, arr._length_, clip, byref(result))

    return result


def interesect_rect_and_line(rect, x1, y1, x2, y2):
    pass


intersects.argtypes = (c_void_p, c_void_p)
intersects.restype = c_bool
_EnclosePoints.argtypes = [
    ctypes.Array,
    c_int32,
    ctypes.POINTER(Rect),
    ctypes.POINTER(Rect)
]
