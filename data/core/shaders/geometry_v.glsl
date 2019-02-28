//GLSL
#version 130
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec3 p3d_Tangent;
in vec3 p3d_Binormal;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat3 p3d_NormalMatrix;

out vec2 UV;
out vec3 T;
out vec3 B;
out vec3 N;
out vec3 TS_V;
//out vec4 V;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    vec4 world_pos = p3d_ModelMatrix * p3d_Vertex;
    T=mat3(p3d_ModelViewMatrix) * p3d_Tangent;
    B=mat3(p3d_ModelViewMatrix) * p3d_Binormal;
    N=p3d_NormalMatrix * p3d_Normal;
    mat3 TBN = transpose(mat3(T,B,N));
    vec4 V=p3d_ModelViewMatrix * p3d_Vertex;
    TS_V = TBN * V.xyz;
    UV = p3d_MultiTexCoord0;
    }
