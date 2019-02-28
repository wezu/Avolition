//GLSL
#version 130
in vec2 uv;
uniform sampler2D forward_tex;
uniform sampler2D input_tex;
#ifndef DISABLE_LUT
uniform sampler2D lut_tex;
#endif

//uniform sampler2D forward_aux_tex;
//uniform vec2 win_size;

vec3 applyColorLUT(sampler2D lut, vec3 color)
    {
    float lutSize = float(textureSize(lut, 0).y);
    color = clamp(color, vec3(0.5 / lutSize), vec3(1.0 - 0.5 / lutSize));
    vec2 texcXY = vec2(color.r * 1.0 / lutSize, 1.0 - color.g);

    int frameZ = int(color.b * lutSize);
    float offsZ = fract(color.b * lutSize);

    vec3 sample1 = textureLod(lut, texcXY + vec2((frameZ) / lutSize, 0), 0).rgb;
    vec3 sample2 = textureLod(lut, texcXY + vec2( (frameZ + 1) / lutSize, 0), 0).rgb;

    return mix(sample1, sample2, offsZ);
    }

void main()
    {
    //vec2 final_uv=uv+ (texture(forward_aux_tex, uv).rg);
    vec4 color_deferred=texture(input_tex,uv);
    vec4 color_forward=texture(forward_tex,uv);

    #ifndef DISABLE_LUT
    color_deferred.rgb=applyColorLUT(lut_tex, color_deferred.rgb);
    #endif

    vec3 final_color=mix(color_deferred.rgb, color_forward.rgb, color_forward.a);

    gl_FragData[0]=vec4(final_color.rgb, 1.0);
    }
