//GLSL
#version 130
uniform sampler2D base_ssr;
uniform sampler2D normal_tex;
uniform sampler2D albedo_tex;
uniform sampler2D noise_tex;
uniform float blur;

in vec2 uv;

void main()
    {
    vec2 win_size=textureSize(base_ssr, 0).xy;

    vec4 normal_roughness_metallic=texture(normal_tex,uv);
    float roughness =pow(normal_roughness_metallic.b, 1.5);
    float metallic=normal_roughness_metallic.a;

    vec2 pixel = vec2(1.0, 1.0)/win_size;
    vec2 sharp=pixel*blur*roughness;

    //vec2 sharp=clamp(pixel*blur, vec2(0.0), vec2((1.0-gloss)*0.08));
    vec4 noise=texture(noise_tex,(win_size*uv/64.0));
    sharp+=(noise.rg*2.0-1.0)*roughness*0.015;


    vec4 out_tex= texture(base_ssr, uv);
    //Hardcoded blur
    out_tex += texture(base_ssr, uv+vec2(-0.326212,-0.405805)*sharp);
    out_tex += texture(base_ssr, uv+ vec2(-0.840144, -0.073580)*sharp);
    out_tex += texture(base_ssr, uv+vec2(-0.695914,0.457137)*sharp);
    out_tex += texture(base_ssr, uv+vec2(-0.203345,0.620716)*sharp);
    out_tex += texture(base_ssr, uv+vec2(0.962340,-0.194983)*sharp);
    out_tex += texture(base_ssr, uv+vec2(0.473434,-0.480026)*sharp);
    out_tex += texture(base_ssr, uv+vec2(0.519456,0.767022)*sharp);
    out_tex += texture(base_ssr, uv+vec2(0.185461,-0.893124)*sharp);
    out_tex += texture(base_ssr, uv+vec2(0.507431,0.064425)*sharp);
    out_tex += texture(base_ssr, uv+vec2(0.896420,0.412458)*sharp);
    out_tex += texture(base_ssr, uv+vec2(-0.321940,-0.932615)*sharp);
    out_tex += texture(base_ssr, uv+vec2(-0.791559,-0.597705)*sharp);
    out_tex/=13.0;
    //out_tex=vec4(gloss, 0.0, 0.0, 1.0);
    //out_tex*=clamp(metallic+(1.0-roughness)*0.5, 0.0, 1.0);

    vec3 tint=texture(albedo_tex,uv).rgb;
    out_tex.rgb*=mix(vec3(0.0), tint, metallic)*(1.0-roughness);

    gl_FragData[0] = out_tex;
    }

