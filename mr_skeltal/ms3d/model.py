import contextlib

import numpy as np
from OpenGL.GL import *  # noqa: F403

from .. import texture
from ..decorator import reify
from ..shaders.skin import SkinShader
from . import Bone, Triangle, Group, Vertex, MS3DSpec


file_spec = MS3DSpec()


@contextlib.contextmanager
def vertex_attributes(*attributes):
    for attr in attributes:
        glEnableVertexAttribArray(attr)
    yield
    for attr in reversed(attributes):
        glDisableVertexAttribArray(attr)


def _handle_vertex(vert, vert_ex):
    return (
        [*vert_ex['weights'], 1.0 - sum(vert_ex['weights'])],
        [vert['bone_id'], *vert_ex['bone_ids']]
    )


class MS3DModel(object):
    def __init__(self, model_path):
        with open(model_path, 'rb') as fp:
            data = file_spec.deserialize(fp)

        self.animation_fps = data['animation_fps']
        self.total_frames = data['total_frames']
        self.current_time = data['current_time']
        self.bones = []
        self.vertices = []
        self.triangles = []
        self.groups = []
        self._timestamp = 0.0

        self.bones.extend(Bone(**bone) for bone in data['joints'])
        # Build up a joint tree
        bone_map = {bone.name: bone for bone in self.bones}
        for name, bone in bone_map.items():
            if not bone.parent_name:
                continue
            bone.parent_bone = bone_map[bone.parent_name]
            bone.parent_bone.children.append(bone)

        for vert, vert_ex in zip(data['vertices'], data['vertices_ex']):
            weights, indices = _handle_vertex(vert, vert_ex)
            self.vertices.append(Vertex(vert['vertex'], weights, indices))

        for tri in data['triangles']:
            self.triangles.append(Triangle([
                self.vertices[idx] for idx in tri['vertex_indices']
            ], tri['vertex_normals'], list(zip(tri['s'], tri['t']))))

        for group in data['groups']:
            self.groups.append(Group(group['name'], [
                self.triangles[idx] for idx in group['triangle_indices']
            ], 0))

        self.shader = SkinShader(num_joints=len(self.bones))

    @reify
    def matrix(self):
        return np.identity(4, dtype=np.float32)

    @property
    def bone_matrices(self):
        return np.array([
            bone.matrix_at_t(self.timestamp) @ bone.inverse_matrix
            for bone in self.bones
        ], dtype=np.float32)

    def render(self, view_matrix, projection_matrix):
        shader = self.shader
        mv_matrix = view_matrix @ self.matrix

        glUseProgram(self.shader.program)
        with vertex_attributes(
            shader.vertices, shader.texcoords,
            shader.bone_ids, shader.bone_weights
        ):
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glUniform1i(self.shader.texture, 0)
            glUniformMatrix4fv(
                self.shader.model_view_matrix, 1, GL_TRUE, mv_matrix
            )
            glUniformMatrix4fv(
                self.shader.projection_matrix, 1, GL_TRUE, projection_matrix
            )
            glUniformMatrix4fv(
                self.shader.bone_matrices,
                len(self.bones), GL_TRUE,
                self.bone_matrices
            )

            for group in self.groups:
                glVertexAttribPointer(
                    self.shader.bone_ids,
                    4, GL_SHORT, GL_FALSE, 0,
                    group.bone_id_buffer
                )
                glVertexAttribPointer(
                    self.shader.bone_weights,
                    4, GL_FLOAT, GL_FALSE, 0,
                    group.bone_weight_buffer
                )
                glVertexAttribPointer(
                    self.shader.vertices,
                    3, GL_FLOAT, GL_FALSE, 0,
                    group.vertex_buffer
                )
                glVertexAttribPointer(
                    self.shader.texcoords,
                    2, GL_FLOAT, GL_FALSE, 0,
                    group.texcoord_buffer
                )

                glDrawArrays(GL_TRIANGLES, 0, len(group.vertex_buffer))

    @property
    def animation_length(self):
        t = 0.0
        for bone in self.bones:
            t = max(
                t,
                bone.rotation_keyframes.max_time,
                bone.translation_keyframes.max_time
            )
        return t

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, t):
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
