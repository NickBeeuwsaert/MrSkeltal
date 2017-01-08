class Vertex(object):
    __slots__ = ['coords', 'bone_weights', 'bone_ids']

    def __init__(self, coords, bone_weights, bone_ids):
        self.coords = coords
        self.bone_weights = bone_weights
        self.bone_ids = bone_ids
