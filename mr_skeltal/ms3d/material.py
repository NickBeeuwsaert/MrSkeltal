from ..decorator import reify
from .. import texture

class Material(object):

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
        self._texture = texture
        self._alphamap = alphamap

    @reify
    def texture(self):
        # Load the models texture, or, if the texture name is empty,
        # Load the test UV grid
        return texture.load(self._texture or 'textures/uv.png')

    @reify
    def alphamap(self):
        return texture.load(self._alphamap)
