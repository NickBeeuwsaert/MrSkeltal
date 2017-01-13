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
        keyframes={}
    ):
        self.name = name
        self.parent_name = parent_name
        self.rotation = rotation
        self.position = position
        self.children = []

        self.rotation_keyframes = Keyframes([
            (keyframe['time'], keyframe['rotation'])
            for keyframe in keyframes.get('rotation') or [
                dict(time=0.0, rotation=(0, 0, 0))
            ]
        ])

        self.translation_keyframes = Keyframes([
            (keyframe['time'], keyframe['translation'])
            for keyframe in keyframes.get('translation') or [
                dict(time=0.0, translation=(0, 0, 0))
            ]
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
            mat = np.dot(self.parent_bone.matrix, mat)
        return mat

    @reify
    def inverse_matrix(self):
        mat = self.inverse_local_matrix
        if self.parent_bone:
            mat = np.dot(mat, self.parent_bone.inverse_matrix)
        return mat

    def rotation_matrix_at_t(self, t):
        return matrix.rotation(self.rotation_keyframes.frame_at_time(t))

    def translation_matrix_at_t(self, t):
        return matrix.translate(self.translation_keyframes.frame_at_time(t))

    def local_matrix_at_t(self, t):
        return np.dot(
            self.translation_matrix_at_t(t), self.rotation_matrix_at_t(t)
        )

    def matrix_at_t(self, t):
        mat = np.dot(self.local_matrix, self.local_matrix_at_t(t))

        if self.parent_bone:
            mat = np.dot(self.parent_bone.matrix_at_t(t), mat)

        return mat
