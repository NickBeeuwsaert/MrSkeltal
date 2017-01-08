import numpy as np
from PIL import Image
from OpenGL.GL import *  # noqa: F403


def load(file_path):
    img = Image.open(file_path, 'r').convert('RGB')

    img_data = np.array(img, dtype=np.uint8)
    width, height = img.size

    texture = glGenTextures(1)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexImage2D(
        GL_TEXTURE_2D, 0,
        GL_RGB, width, height, 0,
        GL_RGB, GL_UNSIGNED_BYTE, img_data
    )

    return texture
