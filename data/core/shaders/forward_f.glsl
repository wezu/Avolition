//GLSL
#version 130
in vec2 UV;
in vec3 N;
uniform sampler2D p3d_Texture0; //rgba color texture
uniform sampler2D depth_tex;

void main()
    {
    vec2 win_size=textureSize(depth_tex, 0).xy;
    vec4 color_map=texture(p3d_Texture0, UV);
    vec2 screen_uv=gl_FragCoord.xy/win_size;
    float depth=texture(depth_tex, screen_uv).r;
    vec3 n=normalize(N);
    if (depth <  gl_FragCoord.z)
        discard;
    gl_FragData[0]=color_map;
    gl_FragData[1]=vec4(n, 0.0);
    }
