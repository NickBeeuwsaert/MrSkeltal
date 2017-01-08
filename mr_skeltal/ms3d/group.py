from functools import lru_cache

import numpy as np

from ..decorator import reify


class Group(object):
    # __slots__ = ['name', 'triangles', 'material']

    def __init__(self, name, triangles, material):
        self.name = name
        self.triangles = triangles
        self.material = material

    @reify
    def vertex_buffer(self):
        vertices = []
        for triangle in self.triangles:
            for vertex in triangle.vertices:
                vertices.append(vertex.coords)

        return np.array(vertices, dtype=np.float32)

    @reify
    def bone_weight_buffer(self):
        bone_weights = []
        for triangle in self.triangles:
            for vertex in triangle.vertices:
                bone_weights.append(vertex.bone_weights)

        return np.array(bone_weights, dtype=np.float32)

    @reify
    def bone_id_buffer(self):
        bone_ids = []
        for triangle in self.triangles:
            for vertex in triangle.vertices:
                bone_ids.append(vertex.bone_ids)

        return np.array(bone_ids, dtype=np.int16)

    @reify
    def normal_buffer(self):
        return np.array([
            triangle.normals
            for triangle in self.triangles
        ], dtype=np.float32)

    @reify
    def texcoord_buffer(self):
        return np.array([
            triangle.texcoords
            for triangle in self.triangles
        ], dtype=np.float32)

    def vertex_iter(self):
        for triangle in self.triangles:
            yield from triangle.vertices

    @lru_cache(None)
    def vertex_buffer_at_t(self, t):
        vertices = []

        for vertex in self.vertex_iter():
            new_vert = np.array([0, 0, 0, 0], dtype=np.float32)
            x, y, z = vertex.coords
            for bone, weight in zip(vertex.bones, vertex.bone_weights):
                if not bone:
                    continue
                new_vert += np.dot(
                    bone.matrix_at_t(t) @ bone.inverse_matrix,
                    np.array([x, y, z, 1], dtype=np.float32)
                ) * weight

            vertices.append(new_vert[:3])

        return np.array(vertices, dtype=np.float32)
