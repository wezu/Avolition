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

//hw animation
in vec4 transform_weight;
in uvec4 transform_index;
uniform mat4 p3d_TransformTable[100];

out vec2 UV;
out vec3 T;
out vec3 B;
out vec3 N;
out vec3 TS_V;
//out vec4 V;

void main()
    {
    //hardware skinning
    mat4 matrix = p3d_TransformTable[transform_index.x] * transform_weight.x
              + p3d_TransformTable[transform_index.y] * transform_weight.y
              + p3d_TransformTable[transform_index.z] * transform_weight.z
              + p3d_TransformTable[transform_index.w] * transform_weight.w;

    vec4 vert=matrix * p3d_Vertex;
    //workaround for driver crash (?)
    mat3 matrix3=mat3(matrix);

    vec3 normal=matrix3*p3d_Normal;
    vec3 tangent=matrix3*p3d_Tangent;
    vec3 binormal =matrix3*p3d_Binormal;

    gl_Position = p3d_ModelViewProjectionMatrix * vert;

    vec4 world_pos = p3d_ModelMatrix * vert;

    T=mat3(p3d_ModelViewMatrix) * tangent;
    B=mat3(p3d_ModelViewMatrix) * binormal;
    N=p3d_NormalMatrix * normal;

    mat3 TBN = transpose(mat3(T,B,N));
    vec4 V=p3d_ModelViewMatrix * vert;
    TS_V = TBN * V.xyz;

    UV = p3d_MultiTexCoord0;
    }
