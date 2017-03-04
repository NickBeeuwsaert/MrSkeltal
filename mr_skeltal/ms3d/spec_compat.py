import struct

from .. import destruct


int8_t = destruct.Number('b', byte_order='<')
uint8_t = destruct.Number('B', byte_order='<')

int16_t = destruct.Number('h', byte_order='<')
uint16_t = destruct.Number('H', byte_order='<')

int32_t = destruct.Number('i', byte_order='<')
uint32_t = destruct.Number('I', byte_order='<')

float_t = destruct.Number('f', byte_order='<')

vec3 = destruct.Tuple(float_t, float_t, float_t)


class VertexStruct(destruct.Struct):
    __types__ = [
        ('flags', uint8_t),
        ('vertex', vec3),
        ('bone_id', int8_t),
        ('reference_count', uint8_t)
    ]


class TriangleStruct(destruct.Struct):
    __types__ = [
        ('flags', uint16_t),
        ('vertex_indices', destruct.Tuple(uint16_t, uint16_t, uint16_t)),
        ('vertex_normals', destruct.Tuple(vec3, vec3, vec3)),
        ('s', destruct.Tuple(float_t, float_t, float_t)),
        ('t', destruct.Tuple(float_t, float_t, float_t)),
        ('smoothing_group', uint8_t),
        ('group_index', uint8_t),
    ]


class GroupStruct(destruct.Struct):
    __types__ = [
        ('flags', uint8_t),
        ('name', destruct.String(32)),
        ('triangle_indices', destruct.Sequence(uint16_t, uint16_t)),
        ('material_index', int8_t)
    ]


class MaterialStruct(destruct.Struct):
    __types__ = [
        ('name', destruct.String(32)),
        ('ambient', destruct.Tuple(float_t, float_t, float_t, float_t)),
        ('diffuse', destruct.Tuple(float_t, float_t, float_t, float_t)),
        ('specular', destruct.Tuple(float_t, float_t, float_t, float_t)),
        ('emissive', destruct.Tuple(float_t, float_t, float_t, float_t)),
        ('shininess', float_t),
        ('transparency', float_t),
        ('mode', int8_t),
        ('texture', destruct.String(128)),
        ('alphamap', destruct.String(128)),
    ]


class RotationKeyframeStruct(destruct.Struct):
    __types__ = [
        ('time', float_t),
        ('rotation', vec3),
    ]


class TranslationKeyframeStruct(destruct.Struct):
    __types__ = [
        ('time', float_t),
        ('translation', vec3)
    ]


class KeyframeStruct(destruct.Type):
    __types__ = [
        ('rotation', RotationKeyframeStruct()),
        ('translation', TranslationKeyframeStruct())
    ]

    def deserialize(self, fp):
        s = struct.Struct('<HH')
        frame_counts = s.unpack(fp.read(s.size))

        return {
            name: [
                child.deserialize(fp) for _ in range(count)
            ] for (name, child), count in zip(self.children, frame_counts)
        }


class JointStruct(destruct.Struct):
    __types__ = [
        ('flags', uint8_t),
        ('name', destruct.String(32)),
        ('parent_name', destruct.String(32)),
        ('rotation', vec3),
        ('position', vec3),
        ('keyframes', KeyframeStruct()),
    ]


class CommentStruct(destruct.Struct):
    __types__ = [
        ('index', uint32_t),
        ('comment', destruct.DynamicString(int32_t)),
    ]


class CommentsStruct(destruct.Struct):
    __types__ = [
        ('sub_version', int32_t),
        ('group', destruct.Sequence(uint32_t, CommentStruct())),
        ('material', destruct.Sequence(uint32_t, CommentStruct())),
        ('joint', destruct.Sequence(uint32_t, CommentStruct())),
        ('model', destruct.Sequence(uint32_t, CommentStruct())),
    ]


class FloatButReallyItsAnInteger(destruct.Type):
    def __init__(self, storage_type, max_value):
        destruct.Type.__init__(self)
        self.storage_type = storage_type
        self.max_value = max_value

    def deserialize(self, fp):
        return self.storage_type.deserialize(fp) / self.max_value

    def serialize(self, data, fp):
        self.storage_type.serialize(int(data * self.max_value), fp)


class ExtendedVertexStructV1(destruct.Struct):
    __types__ = [
        ('bone_ids', destruct.Tuple(int8_t, int8_t, int8_t)),
        ('weights', destruct.Tuple(
            FloatButReallyItsAnInteger(uint8_t, 255),
            FloatButReallyItsAnInteger(uint8_t, 255),
            FloatButReallyItsAnInteger(uint8_t, 255)
        ))
    ]


class ExtendedVertexStructV2(destruct.Struct):
    __types__ = [
        ('bone_ids', destruct.Tuple(int8_t, int8_t, int8_t)),
        ('weights', destruct.Tuple(
            FloatButReallyItsAnInteger(uint8_t, 100),
            FloatButReallyItsAnInteger(uint8_t, 100),
            FloatButReallyItsAnInteger(uint8_t, 100)
        )),
        ('extra', uint32_t),
    ]


def extended_vertex_struct(subversion):
    if subversion == 1:
        return ExtendedVertexStructV1()

    if subversion == 2:
        return ExtendedVertexStructV2()

    raise ValueError('Invalid Subversion for extended vertices')


class ExtendedJointStructV1(destruct.Struct):
    __types__ = [
        ('color', destruct.Tuple(float_t, float_t, float_t))
    ]


class ExtendedModelStructV1(destruct.Struct):
    __types__ = [
        ('joint_size', float_t),
        ('transparency_mode', int32_t),
        ('alpha_ref', float_t)
    ]


class MS3DSpec(destruct.Struct):
    __types__ = [
        ('signature', destruct.Signature(b'MS3D000000')),
        ('version', int32_t),

        ('vertices', destruct.Sequence(uint16_t, VertexStruct())),
        ('triangles', destruct.Sequence(uint16_t, TriangleStruct())),
        ('groups', destruct.Sequence(uint16_t, GroupStruct())),
        ('materials', destruct.Sequence(uint16_t, MaterialStruct())),

        ('animation_fps', float_t),
        ('current_time', float_t),
        ('total_frames', int32_t),

        ('joints', destruct.Sequence(uint16_t, JointStruct())),

        ('comments', CommentsStruct()),
    ]

    def deserialize(self, fp):
        data = super().deserialize(fp)

        sub_version = uint32_t.deserialize(fp)

        vertex_ex = extended_vertex_struct(sub_version)
        data['vertices_ex'] = [
            vertex_ex.deserialize(fp)
            for vertex in data['vertices']
        ]

        # sub_version = uint32_t.deserialize(fp)
        # extended_joint = ExtendedJointStructV1()
        # data['joint_ex'] = [
        #     extended_joint.deserialize(fp)
        #     for joint in data['joints']
        # ]
        # sub_version = uint32_t.deserialize(fp)
        # extended_model = ExtendedModelStructV1()
        # data['model_ex'] = extended_model.deserialize(fp)

        return data
