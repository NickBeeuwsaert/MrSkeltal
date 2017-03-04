# flake8: noqa: F401
import sys

from .group import Group
from .material import Material
from .triangle import Triangle
from .vertex import Vertex
from .bone import Bone
from .shaders import (
    SkinShader,
    SimpleShader
)
if sys.version_info < (3, 6):
    from .spec_compat import MS3DSpec
else:
    from .spec import MS3DSpec
from .model import MS3DModel
