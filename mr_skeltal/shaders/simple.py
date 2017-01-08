from textwrap import dedent

from . import Uniform, Attribute, Shader


class SimpleShader(Shader):
    vertex_shader = dedent("""\
        #version 120
        uniform mat4 uMVMatrix;
        uniform mat4 uPMatrix;

        attribute vec4 aVertex;
        attribute vec2 aTexCoord;
        // attribute vec4 aNormal;

        varying vec2 vTexCoord;

        void main(void) {
            vTexCoord = aTexCoord;
            gl_Position = uPMatrix * uMVMatrix * aVertex;
        }""")

    fragment_shader = dedent("""\
        uniform sampler2D uTexture;

        varying vec2 vTexCoord;
        void main() {
            gl_FragColor = texture2D(uTexture, vTexCoord);
        }""")

    model_view_matrix = Uniform('uMVMatrix')
    projection_matrix = Uniform('uPMatrix')
    texture = Uniform('uTexture')

    vertices = Attribute('aVertex')
    texcoords = Attribute('aTexCoord')
