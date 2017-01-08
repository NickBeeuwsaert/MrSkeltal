import struct

from .. import destruct


class LittleEndianMixin(object):
    byte_order = '<'


int8_t = type('int8_t', (LittleEndianMixin, destruct.Byte), {})
uint8_t = type('uint8_t', (LittleEndianMixin, destruct.UnsignedByte), {})

int16_t = type('int16_t', (LittleEndianMixin, destruct.Short), {})
uint16_t = type('uint16_t', (LittleEndianMixin, destruct.UnsignedShort), {})

int32_t = type('int32_t', (LittleEndianMixin, destruct.Int), {})
uint32_t = type('uint32_t', (LittleEndianMixin, destruct.UnsignedInt), {})

float_t = type('float_t', (LittleEndianMixin, destruct.Float), {})


class vec3(destruct.NamedTuple):
    x = float_t()
    y = float_t()
    z = float_t()


class VertexStruct(destruct.Struct):
    flags = uint8_t()
    vertex = vec3()
    bone_id = int8_t()
    reference_count = uint8_t()


class TriangleStruct(destruct.Struct):
    flags = uint16_t()
    vertex_indices = destruct.Tuple(uint16_t(), uint16_t(), uint16_t())
    vertex_normals = destruct.Tuple(vec3(), vec3(), vec3())
    s = destruct.Tuple(float_t(), float_t(), float_t())
    t = destruct.Tuple(float_t(), float_t(), float_t())
    smoothing_group = uint8_t()
    group_index = uint8_t()


class GroupStruct(destruct.Struct):
    flags = uint8_t()
    name = destruct.String(32)
    triangle_indices = destruct.Sequence(uint16_t(), uint16_t())
    material_index = int8_t()


class MaterialStruct(destruct.Struct):
    name = destruct.String(32)
    ambient = destruct.Tuple(float_t(), float_t(), float_t(), float_t())
    diffuse = destruct.Tuple(float_t(), float_t(), float_t(), float_t())
    specular = destruct.Tuple(float_t(), float_t(), float_t(), float_t())
    emissive = destruct.Tuple(float_t(), float_t(), float_t(), float_t())
    shininess = float_t()
    transparency = float_t()
    mode = int8_t()
    texture = destruct.String(128)
    alphamap = destruct.String(128)


class RotationKeyframeStruct(destruct.Struct):
    time = float_t()
    rotation = vec3()


class TranslationKeyframeStruct(destruct.Struct):
    time = float_t()
    translation = vec3()


class KeyframeStruct(destruct.Type):
    rotation = RotationKeyframeStruct()
    translation = TranslationKeyframeStruct()

    def deserialize(self, fp):
        s = struct.Struct('<HH')
        frame_counts = s.unpack(fp.read(s.size))

        return {
            child.name: [child.deserialize(fp) for _ in range(count)]
            for child, count in zip(self.children, frame_counts)
        }


class JointStruct(destruct.Struct):
    flags = uint8_t()
    name = destruct.String(32)
    parent_name = destruct.String(32)
    rotation = vec3()
    position = vec3()

    keyframes = KeyframeStruct()


class CommentStruct(destruct.Struct):
    index = uint32_t()
    comment = destruct.DynamicString(int32_t())


class CommentsStruct(destruct.Struct):
    sub_version = int32_t()

    group = destruct.Sequence(uint32_t(), CommentStruct())
    material = destruct.Sequence(uint32_t(), CommentStruct())
    joint = destruct.Sequence(uint32_t(), CommentStruct())
    model = destruct.Sequence(uint32_t(), CommentStruct())


class FloatButReallyItsAnInteger(destruct.Type):
    def __init__(self, storage_type, max_value):
        super().__init__()
        self.storage_type = storage_type
        self.max_value = max_value

    def deserialize(self, fp):
        return self.storage_type.deserialize(fp) / self.max_value

    def serialize(self, data, fp):
        self.storage_type.serialize(int(data * self.max_value), fp)


class ExtendedVertexStructV1(destruct.Struct):
    bone_ids = destruct.Tuple(int8_t(), int8_t(), int8_t(), int8_t())
    weights = destruct.Tuple(
        FloatButReallyItsAnInteger(uint8_t(), 255),
        FloatButReallyItsAnInteger(uint8_t(), 255),
        FloatButReallyItsAnInteger(uint8_t(), 255)
    )


class ExtendedVertexStructV2(destruct.Struct):
    bone_ids = destruct.Tuple(int8_t(), int8_t(), int8_t())
    weights = destruct.Tuple(
        FloatButReallyItsAnInteger(uint8_t(), 100),
        FloatButReallyItsAnInteger(uint8_t(), 100),
        FloatButReallyItsAnInteger(uint8_t(), 100)
    )
    extra = uint32_t()


def extended_vertex_struct(subversion):
    if subversion == 1:
        return ExtendedVertexStructV1()

    if subversion == 2:
        return ExtendedVertexStructV2()

    raise ValueError('Invalid Subversion for extended vertices')


class MS3DSpec(destruct.Struct):
    signature = destruct.Signature(b'MS3D000000')
    version = int32_t()

    vertices = destruct.Sequence(uint16_t(), VertexStruct())
    triangles = destruct.Sequence(uint16_t(), TriangleStruct())
    groups = destruct.Sequence(uint16_t(), GroupStruct())
    materials = destruct.Sequence(uint16_t(), MaterialStruct())

    animation_fps = float_t()
    current_time = float_t()
    total_frames = int32_t()

    joints = destruct.Sequence(uint16_t(), JointStruct())

    comments = CommentsStruct()

    def deserialize(self, fp):
        data = super().deserialize(fp)

        sub_version = uint32_t().deserialize(fp)

        vertex_ex = extended_vertex_struct(sub_version)
        data["vertices_ex"] = [
            vertex_ex.deserialize(fp)
            for vertex in data["vertices"]
        ]

        return data
