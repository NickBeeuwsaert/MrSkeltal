from ctypes import c_void_p, c_char_p, c_int32, c_uint32
from enum import IntEnum

from . import SDL


_SetWindowTitle = SDL.SDL_SetWindowTitle
_GetWindowTitle = SDL.SDL_GetWindowTitle
destroy_window = SDL.SDL_DestroyWindow
_CreateWindow = SDL.SDL_CreateWindow


class WindowFlags(IntEnum):
    FULLSCREEN         = 1 << 0                # Fullscreen window
    OPENGL             = 1 << 1                # Window with OpenGL context
    SHOWN              = 1 << 2                # Window is visible
    HIDDEN             = 1 << 3                # Window is hidden
    BORDERLESS         = 1 << 4                # Window has no decoration
    RESIZABLE          = 1 << 5                # Window is resizable
    MINIMIZED          = 1 << 6                # Window starts minimized
    MAXIMIZED          = 1 << 7                # Window starts maximized
    INPUT_GRABBED      = 1 << 8                # input focus
    INPUT_FOCUS        = 1 << 9                # Grab input focus
    MOUSE_FOCUS        = 1 << 10               # Mouse focus
    FULLSCREEN_DESKTOP = FULLSCREEN | 1 << 12  # Fullscreen on a new desktop
    FOREIGN            = 1 << 11               # Window is not created by SDL
    ALLOW_HIGHDPI      = 1 << 13               # High-DPI mode, if available
    MOUSE_CAPTURE      = 1 << 14               # Capture the mouse
    ALWAYS_ON_TOP      = 1 << 15               # Window is always on top
    SKIP_TASKBAR       = 1 << 16               # Don't appear in taskbar
    UTILITY            = 1 << 17               # Render as a Utility window
    TOOLTIP            = 1 << 18               # Tooltip window
    POPUP_MENU         = 1 << 19               # Popup window


def WINDOWPOS_UNDEFINED_DISPLAY(display):
    return 0x1FFF0000 | display


def WINDOWPOS_CENTERED_DISPLAY(display):
    return 0x2FFF0000 | display


class WindowPos(IntEnum):
    UNDEFINED = WINDOWPOS_UNDEFINED_DISPLAY(0)
    CENTERED  = WINDOWPOS_CENTERED_DISPLAY(0)


def get_title(window):
    return _GetWindowTitle(window).decode('utf-8')


def set_title(window, title):
    return _SetWindowTitle(window, title.encode('utf-8'))


class Window(c_void_p):
    title = property(get_title, set_title)


def create_window(title, position, flags):
    x, y, width, height = position

    return _CreateWindow(
        title.encode('utf-8'),
        x, y, width, height,
        flags
    )


_CreateWindow.restype = Window
_CreateWindow.argtypes = (
    c_char_p, c_int32, c_int32, c_int32, c_int32, c_uint32
)
_SetWindowTitle.argtypes = (Window, c_char_p)
_GetWindowTitle.restype = c_char_p
_GetWindowTitle.argtypes = (Window, )
destroy_window.argtypes = (Window, )
