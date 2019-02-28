//GLSL
#version 130
// This parameters should be configured according to Far and Near plane
// of your main camera
const float zFar = 200.0;
const float zNear = 1.0;
//const float maxDelta = 0.01;   // Delta depth test value
//const float rayLength =0.02;   // 0..1 Ray length (percent of zFar)
//const int stepsCount = 16;      // Quality. With too match value may
                                // be problem on non-nvidia cards

//const float fade = 0.7;         // Fade out reflection

in vec2 uv;

uniform sampler2D normal_tex;
uniform sampler2D depth_tex;
uniform sampler2D final_light;
uniform samplerCube cube_tex;
uniform mat4 trans_apiclip_of_camera_to_apiview_of_camera;
uniform mat4 trans_apiview_of_camera_to_apiclip_of_camera;
uniform mat4 trans_apiview_of_camera_to_world;


//uniform float maxDelta;
//uniform float rayLength;


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

float linearizeDepth(float depth)
    {
    return (2.0 * zNear) / (zFar + zNear - depth * (zFar - zNear));
    }


vec4 raytrace(vec3 startPos,
              vec3 endPos,
              mat4 mat_proj,
              sampler2D albedo,
              sampler2D depth)
    {
    // Convert start and end positions of reflect vector from the
    // camera space to the screen space
    vec4 startPosSS = mat_proj * vec4(startPos,1.0);
    startPosSS /= startPosSS.w;
    startPosSS.xy = startPosSS.xy;
    vec4 endPosSS =mat_proj * vec4(endPos,1.0);
    endPosSS /= endPosSS.w;
    endPosSS.xy = endPosSS.xy;
    // Reflection vector in the screen space
    //vec3 vectorSS = normalize(endPosSS.xyz - startPosSS.xyz)*0.05; //???
    vec3 vectorSS = vec3(endPosSS.xyz - startPosSS.xyz)/stepsCount;

    // Init vars for cycle
    vec2 samplePos = vec2(0.0, 0.0);// texcoord for the depth and color
    float sampleDepth = 0.0;        // depth from texture
    float currentDepthSS = 0.0;     // current depth calculated with reflection vector in screen space
    float currentDepth = 0.0;       // current depth calculated with reflection vector
    float deltaD = 0.0;
    vec4 color = vec4(0.0, 0.0, 0.0, 1.0);
    for (int i = 1; i < stepsCount; i++)
        {
        samplePos = (startPosSS.xy + vectorSS.xy*i);
        currentDepthSS = startPosSS.z + vectorSS.z*i;
        currentDepth = linearizeDepth(currentDepthSS);
        sampleDepth = linearizeDepth( texture(depth, samplePos).r);
        deltaD = currentDepth - sampleDepth;
        if ( deltaD > 0 && deltaD < maxDelta * currentDepthSS)
            {
            color = texture(albedo, samplePos);
            //color=vec4(vectorSS*100.0, 0.0);
            float f=fade * (1.0 - float(i) / float(stepsCount));
            //color *= f;
            color.a=1.0-f;
            break;
            }
        }
    return color;
    }

vec3 getPosition(vec2 uv)
    {
    float depth=texture(depth_tex,uv).r * 2.0 - 1.0;
    vec4 view_pos = trans_apiclip_of_camera_to_apiview_of_camera * vec4( uv.xy * 2.0 - vec2(1.0), depth, 1.0);
    view_pos.xyz /= view_pos.w;
    return view_pos.xyz;
    }

void main()
    {
    //float gloss = texture(color_tex, uv).a;
    //view space normal, it's a floating point tex,
    //normalized before writing, ready to use
    vec4 normal_roughness_metallic=texture(normal_tex,uv);
    if (normal_roughness_metallic.rb == vec2(0.0))
        gl_FragData[0] =vec4(0.0, 0.0, 0.0, 1.0);
    else
        {
        if (normal_roughness_metallic.a > 0.0)
            {
            //float gloss=normal_map.a;
            vec3 N = unpack_normal_octahedron(normal_roughness_metallic.xy);
            //hardware depth
            float D = texture(depth_tex, uv).r;

            //view pos in camera space
            vec4 P = trans_apiclip_of_camera_to_apiview_of_camera * vec4( uv.xy,  D, 1.0);
            P.xyz /= P.w;
            //view direction
            vec3 V = normalize(P.xyz);
            // Reflection vector in camera space
            vec3 R = normalize(reflect(V, N)) * zFar * rayLength;

            //float co=abs(dot(-V, N));
            vec4 traced=raytrace(P.xyz, P.xyz + R,
                               trans_apiview_of_camera_to_apiclip_of_camera,
                               final_light, depth_tex);


            //direction towards they eye (camera) in the view (eye) space
            vec3 ecEyeDir = normalize(-getPosition(uv.xy));
            //direction towards the camera in the world space
            vec3 wcEyeDir = vec3(trans_apiview_of_camera_to_world * vec4(ecEyeDir, 0.0));
            //surface normal in the world space
            vec3 wcNormal = vec3(trans_apiview_of_camera_to_world * vec4(N, 0.0));
            //reflection vector in the world space. We negate wcEyeDir as the reflect function expect incident vector pointing towards the surface
            vec3 reflectionWorld = reflect(-wcEyeDir, normalize(wcNormal));

            vec4 cube_reflection=texture(cube_tex, reflectionWorld)*0.5;
            vec3 final=mix(traced.rgb, cube_reflection.rgb, traced.a);

            gl_FragData[0] =vec4(final, 1.0);
            }
        else
            gl_FragData[0] =vec4(0.0, 0.0, 0.0, 1.0);
        }

    }

