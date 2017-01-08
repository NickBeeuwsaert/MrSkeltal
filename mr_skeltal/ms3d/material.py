class Material(object):
    __slots__ = [
        'name',
        'ambient', 'diffuse', 'specular', 'emissive',
        'shininess', 'transparency',
        'texture', 'alphamap'
    ]

    def __init__(
        self, name,
        ambient, diffuse, specular, emissive,
        shininess, transparency,
        texture, alphamap
    ):
        self.name = name
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.emissive = emissive
        self.shininess = shininess
        self.transparency = transparency
        self.texture = texture
        self.alphamap = alphamap
