//GLSL
#version 130
uniform sampler2D input_tex;
uniform float blur;

in vec2 uv;

void main()
    {
    vec2 pixel = vec2(1.0, 1.0)/textureSize(input_tex, 0).xy;
    vec2 sharp=pixel*blur;

    vec4 out_tex= texture(input_tex, uv);
    sharp*=out_tex.a;
    sharp*=pow(distance(uv, vec2(0.5, 0.5))+0.3, 2.0);

    //Hardcoded blur
    out_tex += texture(input_tex, uv+vec2(-0.326212,-0.405805)*sharp);
    out_tex += texture(input_tex, uv+ vec2(-0.840144, -0.073580)*sharp);
    out_tex += texture(input_tex, uv+vec2(-0.695914,0.457137)*sharp);
    out_tex += texture(input_tex, uv+vec2(-0.203345,0.620716)*sharp);
    out_tex += texture(input_tex, uv+vec2(0.962340,-0.194983)*sharp);
    out_tex += texture(input_tex, uv+vec2(0.473434,-0.480026)*sharp);
    out_tex += texture(input_tex, uv+vec2(0.519456,0.767022)*sharp);
    out_tex += texture(input_tex, uv+vec2(0.185461,-0.893124)*sharp);
    out_tex += texture(input_tex, uv+vec2(0.507431,0.064425)*sharp);
    out_tex += texture(input_tex, uv+vec2(0.896420,0.412458)*sharp);
    out_tex += texture(input_tex, uv+vec2(-0.321940,-0.932615)*sharp);
    out_tex += texture(input_tex, uv+vec2(-0.791559,-0.597705)*sharp);
    out_tex/=13.0;

    out_tex.a=1.0;

    gl_FragData[0] = out_tex;
    }

