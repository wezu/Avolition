//GLSL
#version 130
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ViewMatrix;
uniform mat4 trans_world_to_apiview_of_camera;
#ifndef NUM_LIGHTS
uniform vec3 direction;
out vec4 light_direction;
#endif
#ifdef NUM_LIGHTS
uniform vec3 direction [NUM_LIGHTS];
out vec4 light_direction[NUM_LIGHTS];
#endif

//out vec2 uv;


void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    //uv=p3d_MultiTexCoord0;
    #ifndef NUM_LIGHTS
    light_direction=trans_world_to_apiview_of_camera*vec4(normalize(direction), 0.0);
    #endif
    #ifdef NUM_LIGHTS
    for (int i=0; i<NUM_LIGHTS; ++i)
            {
            light_direction[i]=trans_world_to_apiview_of_camera*vec4(normalize(direction[i]), 0.0);
            }
    #endif
    }
