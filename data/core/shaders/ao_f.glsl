//GLSL
#version 130

uniform sampler2D normal_tex;
uniform sampler2D depth_tex;
uniform sampler2D random_tex;
uniform float sample_rad;
uniform float strength;
uniform float falloff;
uniform float amount;

// For each component of v, returns -1 if the component is < 0, else 1
vec2 sign_not_zero(vec2 v)
    {
    // Version with branches (for GLSL < 4.00)
    return vec2(v.x >= 0 ? 1.0 : -1.0, v.y >= 0 ? 1.0 : -1.0);
    }

// Unpacking from octahedron normals, input is the output from pack_normal_octahedron
vec3 unpack_normal_octahedron(vec2 packed_nrm)
    {
    // Version using newer GLSL capatibilities
    vec3 v = vec3(packed_nrm.xy, 1.0 - abs(packed_nrm.x) - abs(packed_nrm.y));
    // Branch-Less version
    v.xy = mix(v.xy, (1.0 - abs(v.yx)) * sign_not_zero(v.xy), step(v.z, 0));
    return normalize(v);
    }


void main()
    {
    const vec3 sphere[16] = vec3[16](vec3(0.53812504, 0.18565957, -0.43192),vec3(0.13790712, 0.24864247, 0.44301823),vec3(0.33715037, 0.56794053, -0.005789503),vec3(-0.6999805, -0.04511441, -0.0019965635),vec3(0.06896307, -0.15983082, -0.85477847),vec3(0.056099437, 0.006954967, -0.1843352),vec3(-0.014653638, 0.14027752, 0.0762037),vec3(0.010019933, -0.1924225, -0.034443386),vec3(-0.35775623, -0.5301969, -0.43581226),vec3(-0.3169221, 0.106360726, 0.015860917),vec3(0.010350345, -0.58698344, 0.0046293875),vec3(-0.08972908, -0.49408212, 0.3287904),vec3(0.7119986, -0.0154690035, -0.09183723),vec3(-0.053382345, 0.059675813, -0.5411899),vec3(0.035267662, -0.063188605, 0.54602677),vec3(-0.47761092, 0.2847911, -0.0271716));

    vec2 win_size=textureSize(depth_tex, 0).xy;
    vec2 uv=gl_FragCoord.xy/win_size;

    float pixel_depth = texture(depth_tex, uv).r;
    vec3 pixel_normal = unpack_normal_octahedron(texture(normal_tex,uv).xy);
    vec3 random_vector = normalize((texture(random_tex, uv * 18.0 + pixel_depth + pixel_normal.xy).xyz * 2.0) - vec3(1.0)).xyz;

    float occlusion = 0.0;
    float radius =sample_rad/pixel_depth;

    float depth_difference;
    vec3 sample_normal;
    vec3 ray;
    for(int i = 0; i < 8; ++i)
        {
        ray = radius * reflect(sphere[i], random_vector);

        sample_normal = unpack_normal_octahedron(texture(normal_tex, uv+ ray.xy).xy);
        depth_difference =  (pixel_depth - texture(depth_tex, uv + ray.xy).r);
        occlusion += step(-strength, depth_difference) * (1.0 - dot(sample_normal.xyz, pixel_normal)) * (1.0 - smoothstep(-strength, falloff, depth_difference));
        }
  //occlusion *= 0.125;// 1/num_samples
  //occlusion=1.0-occlusion;
  //occlusion=0.5+occlusion*0.5;
   // occlusion=1.0-pow(pixel_depth*0.1, 2.0);

  gl_FragData[0]= vec4(1.0-occlusion*0.125*amount, 0.0, 0.0, 0.0);
  //gl_FragData[0]= vec4(occlusion, 0.0, 0.0, 0.0);
}

