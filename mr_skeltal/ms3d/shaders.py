"""MS3D Related shaders.

Shaders customized to work with MS3D Models (specifically, groups, and boneless
models)
"""
from textwrap import dedent

from OpenGL.GL import (
    glUseProgram,
    glEnableVertexAttribArray,
    glDisableVertexAttribArray,
    glVertexAttribPointer,
    glUniform1i, glUniformMatrix4fv,
    glBindTexture,
    glDrawArrays
)
from OpenGL.GL import (
    GL_FALSE, GL_TRUE,
    GL_FLOAT, GL_SHORT,
    GL_TRIANGLES, GL_TEXTURE_2D
)

from ..shader import Uniform, Attribute, Shader


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

    def render(self, model, view_matrix, projection_matrix):
        glUseProgram(self.program)

        glEnableVertexAttribArray(self.texcoords)
        glEnableVertexAttribArray(self.vertices)
        glEnableVertexAttribArray(self.bone_ids)
        glEnableVertexAttribArray(self.bone_weights)

        glBindTexture(GL_TEXTURE_2D, model.texture)
        glUniform1i(self.texture, 0)
        glUniformMatrix4fv(
            self.model_view_matrix, 1, GL_TRUE, view_matrix @ model.matrix
        )
        glUniformMatrix4fv(
            self.projection_matrix, 1, GL_TRUE, projection_matrix
        )
        glUniformMatrix4fv(
            self.bone_matrices, len(model.bones), GL_TRUE, model.bone_matrices
        )

        for group in model.groups:
            glVertexAttribPointer(
                self.bone_ids, 4, GL_SHORT, GL_FALSE, 0, group.bone_id_buffer
            )
            glVertexAttribPointer(
                self.bone_weights, 4, GL_FLOAT, GL_FALSE, 0,
                group.bone_weight_buffer
            )
            glVertexAttribPointer(
                self.vertices, 3, GL_FLOAT, GL_FALSE, 0, group.vertex_buffer
            )
            glVertexAttribPointer(
                self.texcoords, 2, GL_FLOAT, GL_FALSE, 0, group.texcoord_buffer
            )

            glDrawArrays(GL_TRIANGLES, 0, len(group.vertex_buffer))

        glDisableVertexAttribArray(self.bone_weights)
        glDisableVertexAttribArray(self.bone_ids)
        glDisableVertexAttribArray(self.vertices)
        glDisableVertexAttribArray(self.texcoords)


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

    def render(self, model, view_matrix, projection_matrix):
        glUseProgram(self.program)

        glEnableVertexAttribArray(self.texcoords)
        glEnableVertexAttribArray(self.vertices)

        glBindTexture(GL_TEXTURE_2D, model.texture)
        glUniform1i(self.texture, 0)
        glUniformMatrix4fv(
            self.model_view_matrix, 1, GL_TRUE, view_matrix @ model.matrix
        )
        glUniformMatrix4fv(
            self.projection_matrix, 1, GL_TRUE, projection_matrix
        )

        for group in model.groups:
            glVertexAttribPointer(
                self.vertices, 3, GL_FLOAT, GL_FALSE, 0, group.vertex_buffer
            )
            glVertexAttribPointer(
                self.texcoords, 2, GL_FLOAT, GL_FALSE, 0, group.texcoord_buffer
            )

            glDrawArrays(GL_TRIANGLES, 0, len(group.vertex_buffer))

        glDisableVertexAttribArray(self.vertices)
        glDisableVertexAttribArray(self.texcoords)
