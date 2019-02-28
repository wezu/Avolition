//GLSL
#version 130
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;

out vec2 UV;
out vec3 N;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    UV = p3d_MultiTexCoord0;
    N=p3d_NormalMatrix * p3d_Normal;
    }
