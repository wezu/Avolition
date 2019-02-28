//GLSL
#version 130
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewMatrix;

out vec3 N;
out vec3 V;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    N=p3d_NormalMatrix * p3d_Normal;
    V=vec4(p3d_ModelViewMatrix * p3d_Vertex).xyz;
    }
