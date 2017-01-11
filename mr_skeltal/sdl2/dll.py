import ctypes
from ctypes.util import find_library


SDL = ctypes.CDLL(find_library('SDL2'))
