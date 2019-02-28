//GLSL
#version 130
in vec2 UV;
in vec3 N;
in vec4 V;


// For each component of v, returns -1 if the component is < 0, else 1
vec2 sign_not_zero(vec2 v)
    {
    // Version with branches (for GLSL < 4.00)
    return vec2(v.x >= 0 ? 1.0 : -1.0, v.y >= 0 ? 1.0 : -1.0);
    }

// Packs a 3-component normal to 2 channels using octahedron normals
vec2 pack_normal_octahedron(vec3 v)
    {
    // Faster version using newer GLSL capatibilities
    v.xy /= dot(abs(v), vec3(1.0));
    // Branch-Less version
    return mix(v.xy, (1.0 - abs(v.yx)) * sign_not_zero(v.xy), step(v.z, 0.0));
    }



void main()
    {
    vec3 n=normalize(N);

    float roughness=1.0;
    float glow=0.0;
    float metallic=1.0;

    if (distance(V.xy, vec2(0.0, 0.0))<0.7)
        discard;

    gl_FragData[0]=vec4(0.0, 0.0, 0.0, glow);
    gl_FragData[1]=vec4(pack_normal_octahedron(n.xyz), roughness, metallic);
    }
