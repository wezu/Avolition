//GLSL
#version 130
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat4 trans_world_to_apiview_of_camera;
uniform vec3 direction;

out vec2 uv;
out vec4 light_direction;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uv=p3d_MultiTexCoord0;
    light_direction=trans_world_to_apiview_of_camera*vec4(normalize(direction), 0.0);
    }
