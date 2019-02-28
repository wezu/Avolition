//GLSL
#version 130
uniform sampler2D final_light;
uniform sampler2D normal_tex;
uniform float power;
uniform float desat;
uniform float scale;

in vec2 uv;

vec3 desaturate(vec3 input_color, float amount)
    {
    vec3 gray = vec3(dot(input_color, vec3(0.3, 0.59, 0.11)));
    return mix(input_color, gray, amount);
    }


void main()
    {
    vec4 color=texture(final_light, uv);
    vec3 final_color=desaturate(color.rgb, desat)*color.a;
    final_color=pow(final_color.rgb*scale, vec3(power));
    final_color.rgb/=max(1.0, max(max(final_color.r, final_color.g),final_color.b));
    gl_FragData[0] = vec4(final_color, 1.0);
    }

