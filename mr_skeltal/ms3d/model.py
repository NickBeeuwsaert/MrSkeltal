from collections import OrderedDict as odict

import numpy as np

from .. import texture
from ..decorator import reify
from . import Bone, Triangle, Group, Vertex, MS3DSpec, SkinShader, SimpleShader


file_spec = MS3DSpec()


class MS3DModel(object):
    def __init__(self, model_path):
        with open(model_path, 'rb') as fp:
            data = file_spec.deserialize(fp)

        self.animation_fps = data['animation_fps']
        self.total_frames = data['total_frames']
        self.current_time = data['current_time']
        self.bones = odict()
        self.vertices = []
        self.triangles = []
        self.groups = []
        self._timestamp = 0.0

        self.bones.update([
            (bone['name'], Bone(
                bone['name'],
                bone['parent_name'],
                bone['rotation'],
                bone['position'],
                bone['keyframes']
            )) for bone in data['joints']
        ])

        for bone in self.bones.values():
            if not bone.parent_name:
                continue

            bone.parent_bone = self.bones[bone.parent_name]
            bone.parent_bone.children.append(bone)

        self.vertices += [Vertex(vert['vertex'], [
            *vert_ex['weights'], 1.0 - sum(vert_ex['weights'])
        ], [
            vert['bone_id'], *vert_ex['bone_ids']
        ]) for vert, vert_ex in zip(data['vertices'], data['vertices_ex'])]

        self.triangles += [Triangle([
            self.vertices[idx] for idx in triangle['vertex_indices']
        ], triangle['vertex_normals'], list(
            zip(triangle['s'], triangle['t'])
        )) for triangle in data['triangles']]

        self.groups += [Group(group['name'], [
            self.triangles[idx] for idx in group['triangle_indices']
        ], 0) for group in data['groups']]

        self.shader = (
            SkinShader(len(self.bones)) if self.bones else SimpleShader()
        )

    @reify
    def matrix(self):
        return np.identity(4, dtype=np.float32)

    @property
    def bone_matrices(self):
        return np.array([
            bone.matrix_at_t(self.timestamp) @ bone.inverse_matrix
            for bone in self.bones.values()
        ], dtype=np.float32)

    def render(self, view_matrix, projection_matrix):
        self.shader.render(self, view_matrix, projection_matrix)

    @property
    def animation_length(self):
        t = 0.0
        for bone in self.bones.values():
            t = max(t, bone.rotation_keyframes.max_time, bone.translation_keyframes.max_time)
        return t

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, t):
        if self.animation_length:
            self._timestamp = t % self.animation_length

    @reify
    def texture(self):
        return texture.load('uv.png')

    @reify
    def bbox(self):
        """Return the bbox for the model's initial pose"""
        vertices = np.array([
            vertex.coords for vertex in self.vertices
        ], dtype=np.float32)

        return list(zip(*[(min(v), max(v)) for v in vertices.T]))
