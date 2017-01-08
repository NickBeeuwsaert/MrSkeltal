class Triangle(object):
    __slots__ = ['vertices', 'normals', 'texcoords']

    def __init__(self, vertices, normals, texcoords):
        self.vertices = vertices
        self.normals = normals
        self.texcoords = texcoords
