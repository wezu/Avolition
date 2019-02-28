//GLSL
#version 130
struct p3d_LightSourceParameters
    {
    vec4 position;
    //samplerCube shadowMap;
    };
uniform p3d_LightSourceParameters shadowcaster;
uniform mat4 p3d_ProjectionMatrixInverse;
uniform mat4 p3d_ViewProjectionMatrixInverse;
uniform mat4 p3d_ViewMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform sampler2D albedo_tex;
uniform sampler2D normal_tex;
uniform sampler2D depth_tex;

uniform mat4 trans_render_to_shadowcaster;

uniform vec4 light;

uniform float near;
uniform float bias;

in vec3 N;
in vec3 V;

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
    //vec3 specular = mix(vec3(0.04), albedo, metallic);
    float gloss=350.0*(1.0-roughness);
    vec3 glow=albedo*color_tex.a;
    albedo =mix(albedo, vec3(0.0), metallic);
    float depth=texture(depth_tex,uv).r * 2.0 - 1.0;

    vec3 view_pos =getPosition(uv, depth);

    vec3 color=vec3(0.0);
    vec3 spec=vec3(0.0);
    vec3 L=normalize(shadowcaster.position.xyz-view_pos.xyz);;
    vec3 V=normalize(-view_pos.xyz);
    vec3 H = normalize(V+L);
    float NdotH= max(0.0,dot( N, H));
    float NdotL=max(0.0,dot( N, L));

    vec3 light_color=light.rgb;
    float light_radius=light.w;
    float attenuation=1.0-(pow(distance(view_pos.xyz, shadowcaster.position.xyz), 2.0)/light_radius);
    attenuation=pow(max(0.0, attenuation), 3.0);
    //diffuse
    color+=light_color*NdotL*attenuation;
    //specular
    spec=do_specular(roughness, color_tex.rgb, metallic, NdotH, gloss, base_roughness)*light_color*attenuation;

    float bloom = dot(spec, vec3(1.0))*0.33*0.5;
    vec4 final=vec4((color*albedo)+spec, bloom);

    //shadows
    //vec4 world_pos = p3d_ViewProjectionMatrixInverse * vec4( uv.xy * 2.0 - vec2(1.0), depth, 1.0);
    //vec4 shadow_uv=trans_render_to_shadowcaster*world_pos;
    //shadow_uv.xyz=shadow_uv.xyz/shadow_uv.w;
    //float ldist = max(abs(shadow_uv.x), max(abs(shadow_uv.y), abs(shadow_uv.z)));
    //ldist = ((light_radius+near)/(light_radius-near))+((-2.0*light_radius*near)/(ldist * (light_radius-near)));
    //#ifdef DISABLE_SOFTSHADOW
    //    float shadow= float(texture(shadowcaster.shadowMap, shadow_uv.xyz).r >= (ldist * 0.5 + 0.5)+bias);
    //#endif
    //#ifndef DISABLE_SOFTSHADOW
    //    float shadow=soft_shadow_cube( shadowcaster.shadowMap,  shadow_uv.xyz,  ldist,  bias,  150.0*(1.0-attenuation));
    //#endif
    //final*=shadow;

    gl_FragData[0]=final;

    }
