//GLSL
#version 130
in vec2 uv;
uniform sampler2D forward_tex;
uniform sampler2D final_color;

#ifndef DISABLE_AO
uniform sampler2D ao;
#endif
#ifndef DISABLE_SSR
uniform sampler2D ssr;
#endif
#ifndef DISABLE_BLOOM
uniform sampler2D bloom;
#endif
#ifndef DISABLE_DITHERING
uniform sampler2D noise_tex;
#endif

void main()
    {
    vec4 color=texture(final_color,uv);
    vec2 win_size=textureSize(final_color, 0).xy;
    vec3 final_color=color.rgb;

    #ifndef DISABLE_SSR
    vec4 ssr_tex=texture(ssr,uv);
    final_color+=ssr_tex.rgb;
    #endif


    #ifndef DISABLE_SRGB
    final_color.r=pow(final_color.r, 1.0/2.2);
    final_color.g=pow(final_color.g, 1.0/2.2);
    final_color.b=pow(final_color.b, 1.0/2.2);
    #endif

    #ifndef DISABLE_BLOOM
    vec4 bloom_tex=texture(bloom,uv);
    //final_color=clamp(final_color+bloom_tex.rgb*0.5, final_color, bloom_tex.rgb);
    //final_color+=bloom_tex.rgb*5.5;
    final_color=clamp(final_color+bloom_tex.rgb, final_color, vec3(1.0));
    #endif


    #ifndef DISABLE_AO
    float ao_tex=texture(ao,uv).r;
    final_color.rgb*=ao_tex;
    #endif

    #ifndef DISABLE_DITHERING
    vec4 noise=texture(noise_tex,win_size*uv/64.0);
    final_color+= ((noise.r + noise.g)-0.5)/255.0;
    #endif

    gl_FragData[0]=vec4(final_color.rgb, color.a);
    }
