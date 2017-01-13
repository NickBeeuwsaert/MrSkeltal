from collections import OrderedDict as odict
from operator import itemgetter

import numpy as np

from .. import texture
from ..decorator import reify
from . import (
    Bone, Triangle, Group, Vertex, Material,
    MS3DSpec,
    SkinShader, SimpleShader
)


file_spec = MS3DSpec()


def unpack(data, indices):
    return [data[index] for index in indices]


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
        self.materials = []
        self.groups = []
        self._timestamp = 0.0

        self.bones.update((name, Bone(*bone)) for name, bone in zip(
            map(itemgetter('name'), data['joints']),
            map(itemgetter(
                'name', 'parent_name', 'rotation', 'position', 'keyframes'
            ), data['joints'])
        ))

        for bone in self.bones.values():
            if not bone.parent_name:
                continue

            bone.parent_bone = self.bones[bone.parent_name]
            bone.parent_bone.children.append(bone)

        self.vertices.extend(Vertex(
            vertex,
            list(weights) + [1.0 - sum(weights)], [bone_id] + list(bone_ids)
        ) for (vertex, bone_id), (weights, bone_ids) in zip(
            map(itemgetter('vertex', 'bone_id'), data['vertices']),
            map(itemgetter('weights', 'bone_ids'), data['vertices_ex'])
        ))

        self.triangles.extend(Triangle(
            unpack(self.vertices, indices), normals, list(zip(s, t))
        ) for indices, normals, s, t in map(
            itemgetter('vertex_indices', 'vertex_normals', 's', 't'),
            data['triangles']
        ))

        self.materials.extend(Material(*mat) for mat in map(itemgetter(
            'name', 'ambient', 'diffuse', 'specular', 'emissive',
            'shininess', 'transparency', 'texture', 'alphamap'
        ), data['materials']))

        self.groups.extend(Group(
            name, unpack(self.triangles, indices),
            self.materials[mat_index]
        ) for name, indices, mat_index in map(
            itemgetter('name', 'triangle_indices', 'material_index'),
            data['groups']
        ))

        self.shader = (
            SkinShader(len(self.bones)) if self.bones else SimpleShader()
        )

    @reify
    def matrix(self):
        return np.identity(4, dtype=np.float32)

    @property
    def bone_matrices(self):
        return np.array([
            np.dot(bone.matrix_at_t(self.timestamp), bone.inverse_matrix)
            for bone in self.bones.values()
        ], dtype=np.float32)

    def render(self, view_matrix, projection_matrix):
        self.shader.render(self, view_matrix, projection_matrix)

    @property
    def animation_length(self):
        return max([
            max(
                bone.rotation_keyframes.max_time,
                bone.translation_keyframes.max_time
            )
            for bone in self.bones.values()
        ], default=0.0)

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, t):
        if self.animation_length:
            self._timestamp = t % self.animation_length

    @reify
    def bbox(self):
        """Return the bbox for the model's initial pose"""
        vertices = np.array([
            vertex.coords for vertex in self.vertices
        ], dtype=np.float32)

        return list(zip(*[(min(v), max(v)) for v in vertices.T]))
