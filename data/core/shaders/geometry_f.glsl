//GLSL
#version 130
in vec2 UV;
in vec3 T;
in vec3 B;
in vec3 N;
in vec3 TS_V;
//in vec4 V;

uniform sampler2D tex_diffuse; //rgba color texture
#ifndef DISABLE_NORMALMAP
uniform sampler2D tex_normal; //rgba normal+gloss texture
#endif
uniform sampler2D tex_material; //rgma

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







vec2 occlusionPallaxMapping(vec3 v, vec2 t)
{
    int     nMaxSamples         = 30;
    int     nMinSamples         = 10;
    float   fHeightMapScale     = 0.06;
    int nNumSamples = int(mix(nMaxSamples, nMinSamples, abs(dot(vec3(0.0,0.0,1.0), v))));
    // height of each layer
    float fStepSize = 1.0 / float(nNumSamples);
    // Calculate the parallax offset vector max length.
    // This is equivalent to the tangent of the angle between the
    // viewer position and the fragment location.
    float fParallaxLimit = length(v.xy ) / v.z;
    // Scale the parallax limit according to heightmap scale.
    fParallaxLimit *= fHeightMapScale;
    // Calculate the parallax offset vector direction and maximum offset.
    vec2 vOffsetDir = normalize(v.xy);
    vec2 vMaxOffset = vOffsetDir * fParallaxLimit;
    // Initialize the starting view ray height and the texture offsets.
    float fCurrRayHeight = 1.0;
    vec2 vCurrOffset = vec2(0, 0);
    vec2 vLastOffset = vec2(0, 0);
    vec2 dx = dFdx(t);
    vec2 dy = dFdy(t);
    float fLastSampledHeight = 1;
    float fCurrSampledHeight = 1;
    int nCurrSample = 0;
    while ( nCurrSample < nNumSamples )
    {
        // Sample the heightmap at the current texcoord offset.  The heightmap
        // is stored in the alpha channel of the height/normal map.
        //fCurrSampledHeight = tex2Dgrad( NH_Sampler, IN.texcoord + vCurrOffset, dx, dy ).a;
        fCurrSampledHeight = 1.0-textureGrad(tex_normal, UV + vCurrOffset, dx, dy).a;
        // Test if the view ray has intersected the surface.
        if (fCurrSampledHeight > fCurrRayHeight)
        {
            // Find the relative height delta before and after the intersection.
            // This provides a measure of how close the intersection is to
            // the final sample location.
            float delta1 = fCurrSampledHeight - fCurrRayHeight;
            float delta2 = (fCurrRayHeight + fStepSize) - fLastSampledHeight;
            float ratio = delta1 / (delta1 + delta2);
            // Interpolate between the final two segments to
            // find the true intersection point offset.
            vCurrOffset = ratio * vLastOffset + (1.0 - ratio) * vCurrOffset;
            // Force the exit of the while loop
            nCurrSample = nNumSamples + 1;
        }
        else
        {
            // The intersection was not found.  Now set up the loop for the next
            // iteration by incrementing the sample count,
            nCurrSample ++;
            // take the next view ray height step,
            fCurrRayHeight -= fStepSize;
            // save the current texture coordinate offset and increment
            // to the next sample location,
            vLastOffset = vCurrOffset;
            vCurrOffset += fStepSize * vMaxOffset;
            // and finally save the current heightmap height.
            fLastSampledHeight = fCurrSampledHeight;
        }
    }
    // Calculate the final texture coordinate at the intersection point.
    return UV + vCurrOffset;
}



void main()
    {
    vec3 ts_v = normalize(TS_V);
    vec3 n=normalize(N);
    #ifndef DISABLE_POM
        vec2 final_uv=occlusionPallaxMapping(ts_v, UV);
    #endif
    #ifdef DISABLE_POM
        vec2 final_uv=UV;
    #endif

    vec4 rgma_map=texture(tex_material,final_uv);


    vec4 color_map=texture(tex_diffuse,final_uv);
    if (color_map.a <0.5)
        discard;
    #ifndef DISABLE_NORMALMAP
    vec4 normal_map=texture(tex_normal,final_uv);
    //rescale normal
    vec3 normal=normalize(normal_map.xyz*2.0-1.0);
    n*=normal.z;
    n+=normalize(T)*normal.x;
    n-=normalize(B)*normal.y;
    n=normalize(n);
    #endif
    //float shine=shga_map.r;
    //float shine=clamp((normal_map.a-0.1)*2.0, 0.0, 1.0);
    //float glow=shga_map.b;
    float roughness=rgma_map.r;
    float glow=rgma_map.g;
    float metallic=rgma_map.b;

    gl_FragData[0]=vec4(color_map.rgb, glow);
    //gl_FragData[0]=vec4(1.0, 1.0, 1.0, 1.0);
    gl_FragData[1]=vec4(pack_normal_octahedron(n.xyz), roughness, metallic);
    }
