//GLSL
#version 130
in vec4 p3d_Vertex;
in vec3 p3d_Normal;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 trans_world_to_apiview_of_camera;
uniform vec3 direction;

out vec3 N;
out vec3 V;
out vec4 light_direction;

void main()
    {
    light_direction=trans_world_to_apiview_of_camera*vec4(normalize(direction), 0.0);
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    N=p3d_NormalMatrix * p3d_Normal;
    V=vec4(p3d_ModelViewMatrix * p3d_Vertex).xyz;
    }
