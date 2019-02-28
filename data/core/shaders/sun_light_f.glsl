//GLSL
#version 130
struct p3d_LightSourceParameters
    {
    vec4 color;
    vec4 position;
    vec3 spotDirection;
    float spotExponent;
    float spotCutoff;
    float spotCosCutoff;
    sampler2D shadowMap;
    };
uniform p3d_LightSourceParameters spot;
uniform mat4 p3d_ProjectionMatrixInverse;
uniform sampler2D albedo_tex;
uniform sampler2D normal_tex;
uniform sampler2D depth_tex;

uniform mat4 trans_render_to_clip_of_spot;
uniform mat4 p3d_ViewProjectionMatrixInverse;

uniform float bias;

in vec3 N;
in vec3 V;
in vec4 light_direction;
//in vec4 shadow_uv;

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


// Unpacking from octahedron normals, input is the output from pack_normal_octahedron
vec3 unpack_normal_octahedron(vec2 packed_nrm)
    {
    // Version using newer GLSL capatibilities
    vec3 v = vec3(packed_nrm.xy, 1.0 - abs(packed_nrm.x) - abs(packed_nrm.y));
    // Branch-Less version
    v.xy = mix(v.xy, (1.0 - abs(v.yx)) * sign_not_zero(v.xy), step(v.z, 0));
    return normalize(v);
    }

float soft_shadow(sampler2D tex, vec2 uv, float z, float bias, float blur)
    {
    float result = float(texture(tex, uv + vec2( -0.326212, -0.405805)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(-0.840144, -0.073580)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(-0.695914, 0.457137)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(-0.203345, 0.620716)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(0.962340, -0.194983)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(0.473434, -0.480026)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(0.519456, 0.767022)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(0.185461, -0.893124)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(0.507431, 0.064425)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(0.896420, 0.412458)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(-0.321940, -0.932615)*blur).r >= z+bias);
    result += float(texture(tex, uv + vec2(-0.791559, -0.597705)*blur).r >= z+bias);
    return result/12.0;
    }

void main()
    {
    vec3 color=vec3(0.0, 0.0, 0.0);
    vec2 win_size=textureSize(depth_tex, 0).xy;
    vec2 uv=gl_FragCoord.xy/win_size;

    vec4 color_tex=texture(albedo_tex, uv);
    vec3 albedo=color_tex.rgb;
    vec4 normal_glow_gloss=texture(normal_tex,uv);
    vec3 normal=unpack_normal_octahedron(normal_glow_gloss.xy);
    float gloss=normal_glow_gloss.a;
    float glow=normal_glow_gloss.b;
    float depth=texture(depth_tex,uv).r * 2.0 - 1.0;

    //vec4 light_view_pos=spot.position;

    vec4 view_pos = p3d_ProjectionMatrixInverse * vec4( uv.xy * 2.0 - vec2(1.0), depth, 1.0);
    view_pos.xyz /= view_pos.w;

    //vec3 light_vec = -normalize(spot.spotDirection);
    vec3 light_vec = normalize(light_direction.xyz);
    //light_vec = normalize(spot.position.xyz-view_pos.xyz);

    //diffuse
    color+=spot.color.rgb*max(dot(normal.xyz,light_vec), 0.0);
    //spec
    vec3 view_vec = normalize(-view_pos.xyz);
    vec3 reflect_vec=normalize(reflect(light_vec,normal.xyz));
    float spec=clamp(pow(max(dot(reflect_vec, -view_vec), 0.0), 50.0+1500.0*gloss)*gloss*2.0, 0.0, 0.45);


    vec4 final=vec4((color*albedo)+spot.color.rgb*spec, spec+gloss);

    gl_FragData[0]=final;
    }
