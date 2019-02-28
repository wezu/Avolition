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
    //sampler2D shadowMap;
    };
uniform p3d_LightSourceParameters spot;
uniform mat4 p3d_ProjectionMatrixInverse;
uniform sampler2D albedo_tex;
uniform sampler2D normal_tex;
uniform sampler2D depth_tex;

//uniform mat4 trans_render_to_clip_of_spot;
//uniform mat4 p3d_ViewProjectionMatrixInverse;

//uniform vec2 win_size;
uniform float light_radius;
uniform float light_fov;
uniform vec4 light_pos;
//uniform float near;
//uniform float bias;

in vec3 N;
in vec3 V;
//in vec4 shadow_uv;

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

vec4 blur_tex(sampler2D tex, vec2 uv, float blur)
    {
    vec4 out_tex= texture(tex, uv);
    out_tex += texture(tex, uv+vec2(-0.326212,-0.405805)*blur);
    out_tex += texture(tex, uv+ vec2(-0.840144, -0.073580)*blur);
    out_tex += texture(tex, uv+vec2(-0.695914,0.457137)*blur);
    out_tex += texture(tex, uv+vec2(-0.203345,0.620716)*blur);
    out_tex += texture(tex, uv+vec2(0.962340,-0.194983)*blur);
    out_tex += texture(tex, uv+vec2(0.473434,-0.480026)*blur);
    out_tex += texture(tex, uv+vec2(0.519456,0.767022)*blur);
    out_tex += texture(tex, uv+vec2(0.185461,-0.893124)*blur);
    out_tex += texture(tex, uv+vec2(0.507431,0.064425)*blur);
    out_tex += texture(tex, uv+vec2(0.896420,0.412458)*blur);
    out_tex += texture(tex, uv+vec2(-0.321940,-0.932615)*blur);
    out_tex += texture(tex, uv+vec2(-0.791559,-0.597705)*blur);
    out_tex/=13.0;
    return out_tex;
    }

vec3 getPosition(vec2 uv, float depth)
    {
    vec4 view_pos = p3d_ProjectionMatrixInverse * vec4( uv.xy * 2.0 - vec2(1.0), depth, 1.0);
    view_pos.xyz /= view_pos.w;
    return view_pos.xyz;
    }

vec3 do_specular(float roughness, vec3 tint,
                 float metallic, float NdotH,
                 float gloss, float base_roughness)
    {
    return mix(vec3(1.0-roughness), tint, metallic) * pow(NdotH, gloss)*(1.0-base_roughness+metallic);
    }

void main()
    {
    vec2 win_size=textureSize(depth_tex, 0).xy;
    vec2 uv=gl_FragCoord.xy/win_size;

    vec4 color_tex=texture(albedo_tex, uv);
    vec3 albedo=color_tex.rgb;
    vec4 normal_roughness_metallic=texture(normal_tex,uv);
    vec3 N=unpack_normal_octahedron(normal_roughness_metallic.xy);
    float roughness =pow(normal_roughness_metallic.b, 0.5);
    float base_roughness =normal_roughness_metallic.b;
    float metallic=normal_roughness_metallic.a;
    float gloss=350.0*(1.0-roughness);
    vec3 glow=albedo*color_tex.a;
    albedo =mix(albedo, vec3(0.0), metallic);
    float depth=texture(depth_tex,uv).r * 2.0 - 1.0;

    vec3 view_pos =getPosition(uv, depth);

    vec3 color=vec3(0.0);
    vec3 spec=vec3(0.0);
    vec3 L=normalize(spot.position.xyz-view_pos.xyz);
    vec3 V=normalize(-view_pos.xyz);
    vec3 H = normalize(V+L);
    float NdotH= max(0.0,dot( N, H));
    float NdotL=max(0.0,dot( N, L));

    vec3 light_color=spot.color.rgb;
    float attenuation=1.0-(pow(distance(view_pos.xyz, spot.position.xyz)/light_radius*1.1, 4.0));
    float spotEffect = dot(normalize(spot.spotDirection), -L);
    float falloff=0.0;
    if (spotEffect > spot.spotCosCutoff)
      falloff = pow(spotEffect,spot.spotExponent);
    attenuation*=falloff;

    //diffuse
    color+=light_color*NdotL*attenuation;
    //specular
    spec=do_specular(roughness, color_tex.rgb, metallic, NdotH, gloss, base_roughness)*light_color*attenuation;

    float bloom = dot(spec, vec3(1.0))*0.33*0.5;
    vec4 final=vec4((color*albedo)+spec, bloom);

    //shadows
    //vec4 pos = p3d_ViewProjectionMatrixInverse * vec4( uv.xy * 2.0 - vec2(1.0), depth, 1.0);
    //vec4 shadow_uv=trans_render_to_clip_of_spot*pos;
    //shadow_uv.xyz=shadow_uv.xyz/shadow_uv.w*0.5+0.5;
    //#ifdef DISABLE_SOFTSHADOW
    //float shadow= float(texture(spot.shadowMap, shadow_uv.xy).r >= shadow_uv.z+bias);
    //#endif
    //#ifndef DISABLE_SOFTSHADOW
    //float shadow= soft_shadow(spot.shadowMap, shadow_uv.xy+vec2(0.0, 0.005), shadow_uv.z, bias, 0.003*attenuation);
    //#endif
    //final*=shadow;

    gl_FragData[0]=final;
    }
