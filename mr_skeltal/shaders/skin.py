from textwrap import dedent

from . import Uniform, Attribute, Shader


class SkinShader(Shader):
    vertex_shader = dedent("""\
        #version 120
        uniform mat4 uMVMatrix;
        uniform mat4 uPMatrix;
        uniform mat4 uBoneMatrices[{num_joints}];

        attribute vec3 aVertex;
        attribute vec2 aTexCoord;
        // attribute vec4 aNormal;
        attribute vec4 aBoneIds;
        attribute vec4 aBoneWeights;

        varying vec2 vTexCoord;

        void main(void) {{
            vTexCoord = aTexCoord;
            vec4 newVertex = vec4(0.0);

            ivec4 boneIds = ivec4(aBoneIds);
            for(int idx = 0; idx < 4; idx++) {{
                if(boneIds[idx] == -1) continue;
                newVertex +=
                    uBoneMatrices[boneIds[idx]] *
                    vec4(aVertex, 1.0) *
                    aBoneWeights[idx];
            }}

            gl_Position = uPMatrix * uMVMatrix * vec4(newVertex.xyz, 1.0);
        }}""")

    fragment_shader = dedent("""\
        uniform sampler2D uTexture;

        varying vec2 vTexCoord;
        void main() {
            gl_FragColor = texture2D(uTexture, vTexCoord);
        }""")

    model_view_matrix = Uniform('uMVMatrix')
    projection_matrix = Uniform('uPMatrix')
    bone_matrices = Uniform('uBoneMatrices')
    texture = Uniform('uTexture')

    vertices = Attribute('aVertex')
    texcoords = Attribute('aTexCoord')
    bone_ids = Attribute('aBoneIds')
    bone_weights = Attribute('aBoneWeights')

    def __init__(self, num_joints):
        self.vertex_shader = self.vertex_shader.format(num_joints=num_joints)
        super().__init__()
