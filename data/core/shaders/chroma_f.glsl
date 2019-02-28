//GLSL
#version 130
uniform sampler2D input_tex;

in vec2 uv;

void main()
    {
    vec2 pixel = vec2(1.0, 1.0)/textureSize(input_tex, 0).xy;

    vec3 chroma_distort = vec3(-3.75, 2.5, 7.5) *pow(distance(uv, vec2(0.5, 0.5)), 2.0);

    // cromatic distort:
    vec4 result = vec4(0.0, 0.0, 0.0, 1.0);
    result.r = texture(input_tex, uv +uv*pixel* chroma_distort.x).r;
    result.g = texture(input_tex, uv +uv*pixel* chroma_distort.y).g;
    result.b = texture(input_tex, uv +uv*pixel* chroma_distort.z).b;

    gl_FragData[0] = result;
    }

