//GLSL
#version 130
uniform sampler2D tex;
uniform vec3 config;
uniform vec2 screen_size;
uniform sampler2D depth_tex;

flat in vec2 center;
flat in float point_size;
in vec2 uv_offset;

float linear_depth(float d)
    {
    float f=100.0;
    float n = 1.0;
    return (2.0 * n) / (f + n - d * (f - n));
    }


void main()
    {
    vec2 win_size=textureSize(depth_tex, 0).xy;
    vec2 screen_uv=gl_FragCoord.xy/screen_size;
    float depth=texture(depth_tex, screen_uv).r;
    if (depth+0.001 <  gl_FragCoord.z)
        discard;
    float d=((depth-gl_FragCoord.z)*100.0)+(gl_FragCoord.z*0.85);
    float softness = clamp(d, 0.1, 1.0);

    vec2 uv = (gl_FragCoord.xy / screen_size - center) / (point_size / screen_size) + 0.5;
    uv.y-=1.0;
    float frame_size=config.x;
    uv*=frame_size/textureSize(tex,0).x;
    uv+=uv_offset;
    vec4 final=texture(tex, uv);
    final.a*=softness;
    gl_FragData[0]=final;
    }
