from functools import lru_cache

import numpy as np

from ..decorator import reify
from .. import matrix
from .keyframes import Keyframes


class Bone(object):
    parent_bone = None

    def __init__(
        self,
        name, parent_name,
        rotation, position,
        keyframes={},
        **kwargs
    ):
        self.name = name
        self.parent_name = parent_name
        self.rotation = rotation
        self.position = position
        self.children = []
        self.rotation_keyframes = Keyframes([
            (keyframe['time'], keyframe['rotation'])
            for keyframe in keyframes.get('rotation')
        ])
        self.translation_keyframes = Keyframes([
            (keyframe['time'], keyframe['translation'])
            for keyframe in keyframes.get('translation')
        ])

    @reify
    def rotation_matrix(self):
        return matrix.rotation(self.rotation)

    @reify
    def inverse_rotation_matrix(self):
        return self.rotation_matrix.T

    @reify
    def translation_matrix(self):
        return matrix.translate(self.position)

    @reify
    def inverse_translation_matrix(self):
        return matrix.translate(np.negative(self.position))

    @reify
    def local_matrix(self):
        return np.dot(self.translation_matrix, self.rotation_matrix)

    @reify
    def inverse_local_matrix(self):
        return np.dot(
            self.inverse_rotation_matrix,
            self.inverse_translation_matrix
        )

    @reify
    def matrix(self):
        mat = self.local_matrix
        if self.parent_bone:
            mat = self.parent_bone.matrix @ mat
        return mat

    @reify
    def inverse_matrix(self):
        mat = self.inverse_local_matrix
        if self.parent_bone:
            mat = mat @ self.parent_bone.inverse_matrix
        return mat

    def rotation_matrix_at_t(self, t):
        return matrix.rotation(self.rotation_keyframes.frame_at_time(t))

    def translation_matrix_at_t(self, t):
        return matrix.translate(self.translation_keyframes.frame_at_time(t))

    def local_matrix_at_t(self, t):
        return self.translation_matrix_at_t(t) @ self.rotation_matrix_at_t(t)

    @lru_cache(None)
    def matrix_at_t(self, t):
        mat = self.local_matrix @ self.local_matrix_at_t(t)

        if self.parent_bone:
            mat = self.parent_bone.matrix_at_t(t) @ mat

        return mat
