//GLSL
#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
uniform vec2 screen_size;
uniform sampler2D tex;
uniform vec3 config;
uniform float osg_FrameTime;
uniform float scale;

in vec4 p3d_Vertex;

flat out vec2 center;
flat out float point_size;
out vec2 uv_offset;

void main()
    {
    float size=scale;//p3d_ModelMatrix[0][0];
    float frame_size=config.x;
    float fps=config.y;
    float start_time=config.z;
    vec2 tex_size=textureSize(tex, 0).xy;

    vec4 view_pos= p3d_ModelViewMatrix * p3d_Vertex;
    point_size = (screen_size.y/-view_pos.z)*size;

    gl_PointSize = point_size;
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    center = (gl_Position.xy / gl_Position.w * 0.5 + 0.5);

    float t = floor((osg_FrameTime-start_time)*fps);
    uv_offset.x=mod(t, tex_size.x/frame_size);
    uv_offset.y=-mod((t-uv_offset.x)/(tex_size.y/frame_size), tex_size.y/frame_size);
    uv_offset*=vec2(frame_size)/tex_size;
    }

