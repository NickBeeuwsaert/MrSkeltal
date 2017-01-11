from enum import IntEnum
from sys import byteorder


class PixelType(IntEnum):
    UNKNOWN  =  0
    INDEX1   =  1
    INDEX4   =  2
    INDEX8   =  3
    PACKED8  =  4
    PACKED16 =  5
    PACKED32 =  6
    ARRAYU8  =  7
    ARRAYU16 =  8
    ARRAYU32 =  9
    ARRAYF16 = 10
    ARRAYF32 = 11


class BitmapOrder(IntEnum):
    NONE = 0
    _4321 = 1
    _1234 = 2


class PackedOrder(IntEnum):
    NONE = 0
    XRGB = 1
    RGBX = 2
    ARGB = 3
    RGBA = 4
    XBGR = 5
    BGRX = 6
    ABGR = 7
    BGRA = 8


class ArrayOrder(IntEnum):
    NONE = 0
    RGB  = 1
    RGBA = 2
    ARGB = 3
    BGR  = 4
    BGRA = 5
    ABGR = 6


class PackedLayout(IntEnum):
    NONE     = 0
    _332     = 1
    _4444    = 2
    _1555    = 3
    _5551    = 4
    _565     = 5
    _8888    = 6
    _2101010 = 7
    _1010102 = 8


def PIXELFORMAT(_type, order, layout, bits, _bytes):
    return (
        1 << 28 | _type << 24 | order << 20 |
        layout << 16 | bits << 8 | _bytes << 0
    )


class PixelFormat(IntEnum):
    UNKNOWN     = 0
    INDEX1LSB   = PIXELFORMAT(PixelType.INDEX1, BitmapOrder._4321, 0, 1, 0)
    INDEX1MSB   = PIXELFORMAT(PixelType.INDEX1, BitmapOrder._1234, 0, 1, 0)
    INDEX4LSB   = PIXELFORMAT(PixelType.INDEX4, BitmapOrder._4321, 0, 4, 0)
    INDEX4MSB   = PIXELFORMAT(PixelType.INDEX4, BitmapOrder._1234, 0, 4, 0)
    INDEX8      = PIXELFORMAT(PixelType.INDEX8, 0, 0, 8, 1)
    RGB332      = PIXELFORMAT(
        PixelType.PACKED8, PackedOrder.XRGB, PackedLayout._332, 8, 1
    )
    RGB444      = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.XRGB, PackedLayout._4444, 12, 2
    )
    RGB555      = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.XRGB, PackedLayout._1555, 15, 2
    )
    BGR555      = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.XBGR, PackedLayout._1555, 15, 2
    )
    ARGB4444    = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.ARGB, PackedLayout._4444, 16, 2
    )
    RGBA4444    = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.RGBA, PackedLayout._4444, 16, 2
    )
    ABGR4444    = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.ABGR, PackedLayout._4444, 16, 2
    )
    BGRA4444    = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.BGRA, PackedLayout._4444, 16, 2
    )
    ARGB1555    = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.ARGB, PackedLayout._1555, 16, 2
    )
    RGBA5551    = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.RGBA, PackedLayout._5551, 16, 2
    )
    ABGR1555    = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.ABGR, PackedLayout._1555, 16, 2
    )
    BGRA5551    = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.BGRA, PackedLayout._5551, 16, 2
    )
    RGB565      = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.XRGB, PackedLayout._565, 16, 2
    )
    BGR565      = PIXELFORMAT(
        PixelType.PACKED16, PackedOrder.XBGR, PackedLayout._565, 16, 2
    )
    RGB24       = PIXELFORMAT(PixelType.ARRAYU8, ArrayOrder.RGB, 0, 24, 3)
    BGR24       = PIXELFORMAT(PixelType.ARRAYU8, ArrayOrder.BGR, 0, 24, 3)
    RGB888      = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.XRGB, PackedLayout._8888, 24, 4
    )
    RGBX8888    = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.RGBX, PackedLayout._8888, 24, 4
    )
    BGR888      = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.XBGR, PackedLayout._8888, 24, 4
    )
    BGRX8888    = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.BGRX, PackedLayout._8888, 24, 4
    )
    ARGB8888    = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.ARGB, PackedLayout._8888, 32, 4
    )
    RGBA8888    = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.RGBA, PackedLayout._8888, 32, 4
    )
    ABGR8888    = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.ABGR, PackedLayout._8888, 32, 4
    )
    BGRA8888    = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.BGRA, PackedLayout._8888, 32, 4
    )
    ARGB2101010 = PIXELFORMAT(
        PixelType.PACKED32, PackedOrder.ARGB, PackedLayout._2101010, 32, 4
    )

    RGBA32 = RGBA8888 if byteorder == 'big' else ABGR8888
    ARGB32 = ARGB8888 if byteorder == 'big' else BGRA8888
    BGRA32 = BGRA8888 if byteorder == 'big' else ARGB8888
    ABGR32 = ABGR8888 if byteorder == 'big' else RGBA8888
