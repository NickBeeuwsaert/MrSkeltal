from ctypes import Structure, Union
from ctypes import c_uint32, c_int32, c_uint8, byref
from enum import IntEnum

from . import SDL


class EventType(IntEnum):
    QUIT = 0x100

    KEYDOWN        = 0x300
    KEYUP          = 0x301
    TEXTEDITING    = 0x302
    TEXTINPUT      = 0x303
    KEYMAPCHANAGED = 0x304

    MOUSEMOTION     = 0x400
    MOUSEBUTTONDOWN = 0x401
    MOUSEBUTTONUP   = 0x402
    MOUSEWHEEL      = 0x403


class QuitEvent(Structure):
    _fields_ = [
        ('type', c_uint32),
        ('timestamp', c_uint32),
    ]


class MouseMotionEvent(Structure):
    _fields_ = [
        ('type', c_uint32),
        ('timestamp', c_uint32),
        ('window_id', c_uint32),
        ('which', c_uint32),
        ('state', c_uint32),
        ('x', c_int32),
        ('y', c_int32),
        ('x_rel', c_int32),
        ('y_rel', c_int32)
    ]


class MouseButtonEvent(Structure):
    _fields_ = [
        ('type', c_uint32),
        ('timestamp', c_uint32),
        ('window_id', c_uint32),
        ('which', c_uint32),
        ('button', c_uint8),
        ('state', c_uint8),
        ('clicks', c_uint8),
        ('x', c_int32),
        ('y', c_int32)
    ]


class Event(Union):
    _fields_ = [
        ('type', c_uint32),
        ('motion', MouseMotionEvent),
        ('button', MouseButtonEvent),
        ('quit', QuitEvent),
        ('padding', c_uint8 * 56)
    ]


def poll():
    evt = Event()

    while SDL.SDL_PollEvent(byref(evt)):
        yield evt
