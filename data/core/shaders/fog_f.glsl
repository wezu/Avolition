//GLSL
#version 130
uniform mat4 trans_apiclip_of_camera_to_apiview_of_camera;
uniform sampler2D depth_tex;
uniform sampler2D input_tex;
uniform vec3 fog_color;
uniform float fog_start;
uniform float fog_max;
uniform float dof_near;
uniform float dof_far_start;
uniform float dof_far_max;

in vec2 uv;

const float PI = 3.14159265358;


void main()
    {
    vec4 color=texture(input_tex,uv);

    float depth=texture(depth_tex,uv).r * 2.0 - 1.0;
    vec4 view_pos = trans_apiclip_of_camera_to_apiview_of_camera * vec4( uv.xy * 2.0 - vec2(1.0), depth, 1.0);
    view_pos.xyz /= view_pos.w;

    float dof=pow(min(max(view_pos.z+dof_far_max,0.0)/(dof_far_max-dof_far_start), 1.0), 2.0);
    dof+=pow(min(-view_pos.z/dof_near, 1.0), 2.0)-1.0;

    float fog=pow(min(max(view_pos.z+fog_max,0.0)/(fog_max-fog_start), 1.0), 2.0);

    gl_FragData[0]=vec4(mix(fog_color.rgb, color.rgb, fog),1.0-dof);
    }
