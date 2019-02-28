//GLSL
#version 130
//#extension GL_EXT_gpu_shader4 : enable

uniform sampler2D pre_aa; // 0
uniform float vx_offset;
//uniform vec2 win_size;
uniform float span_max = 8.0;
uniform float reduce_mul = 1.0/8.0;
//uniform float FXAA_SUBPIX_SHIFT = 1.0/4.0;
in vec4 posPos;

#define FxaaInt2 ivec2
#define FxaaFloat2 vec2
#define FxaaTexLod0(t, p) textureLod(t, p, 0.0)
#define FxaaTexOff(t, p, o, r) textureLodOffset(t, p, 0.0, o)
//#define FxaaTexOff(t, p, o, r) texture2D(t, p + o * r)

vec3 FxaaPixelShader(
  vec4 posPos, // Output of FxaaVertexShader interpolated across screen.
  sampler2D tex, // Input texture.
  vec2 rcpFrame) // Constant {1.0/frameWidth, 1.0/frameHeight}.
{
/*---------------------------------------------------------*/
    #define FXAA_REDUCE_MIN   (1.0/128.0)
    //#define reduce_mul   (1.0/8.0)
    //#define span_max     8.0
/*---------------------------------------------------------*/
    vec3 rgbNW = FxaaTexLod0(tex, posPos.zw).xyz;
    vec3 rgbNE = FxaaTexOff(tex, posPos.zw, FxaaInt2(1,0), rcpFrame.xy).xyz;
    vec3 rgbSW = FxaaTexOff(tex, posPos.zw, FxaaInt2(0,1), rcpFrame.xy).xyz;
    vec3 rgbSE = FxaaTexOff(tex, posPos.zw, FxaaInt2(1,1), rcpFrame.xy).xyz;
    vec3 rgbM  = FxaaTexLod0(tex, posPos.xy).xyz;
/*---------------------------------------------------------*/
    vec3 luma = vec3(0.299, 0.587, 0.114);
    float lumaNW = dot(rgbNW, luma);
    float lumaNE = dot(rgbNE, luma);
    float lumaSW = dot(rgbSW, luma);
    float lumaSE = dot(rgbSE, luma);
    float lumaM  = dot(rgbM,  luma);
/*---------------------------------------------------------*/
    float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
    float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));
/*---------------------------------------------------------*/
    vec2 dir;
    dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));
    dir.y =  ((lumaNW + lumaSW) - (lumaNE + lumaSE));
/*---------------------------------------------------------*/
    float dirReduce = max(
        (lumaNW + lumaNE + lumaSW + lumaSE) * (0.25 * reduce_mul),
        FXAA_REDUCE_MIN);
    float rcpDirMin = 1.0/(min(abs(dir.x), abs(dir.y)) + dirReduce);
    dir = min(FxaaFloat2( span_max,  span_max),
          max(FxaaFloat2(-span_max, -span_max),
          dir * rcpDirMin)) * rcpFrame.xy;
/*--------------------------------------------------------*/
    vec3 rgbA = (1.0/2.0) * (
        FxaaTexLod0(tex, posPos.xy + dir * (1.0/3.0 - 0.5)).xyz +
        FxaaTexLod0(tex, posPos.xy + dir * (2.0/3.0 - 0.5)).xyz);
    vec3 rgbB = rgbA * (1.0/2.0) + (1.0/4.0) * (
        FxaaTexLod0(tex, posPos.xy + dir * (0.0/3.0 - 0.5)).xyz +
        FxaaTexLod0(tex, posPos.xy + dir * (3.0/3.0 - 0.5)).xyz);
    float lumaB = dot(rgbB, luma);
    if((lumaB < lumaMin) || (lumaB > lumaMax)) return rgbA;
    return rgbB; }

vec4 PostFX(sampler2D tex, vec2 uv)
{
  vec4 c = vec4(0.0);
  vec2 win_size=textureSize(pre_aa, 0).xy;
  vec2 rcpFrame = vec2(1.0/win_size.x, 1.0/win_size.y);
  c.rgb = FxaaPixelShader(posPos, tex, rcpFrame);
  //c.rgb = 1.0 - texture2D(tex, posPos.xy).rgb;
  c.a = 1.0;
  return c;
}

void main()
{
  gl_FragData[0] = PostFX(pre_aa, posPos.xy);
  //gl_FragColor =texture(pre_aa, posPos.xy);
}
