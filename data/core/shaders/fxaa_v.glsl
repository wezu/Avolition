//GLSL
#version 130
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float subpix_shift = 1.0/4.0;
//uniform vec2 win_size;
uniform sampler2D pre_aa; // 0
out vec4 posPos;

void main()
    {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    vec2 win_size=textureSize(pre_aa, 0).xy;
    vec2 rcpFrame = vec2(1.0/win_size.x, 1.0/win_size.y);
    posPos.xy = p3d_MultiTexCoord0.xy;
    posPos.zw = p3d_MultiTexCoord0.xy - (rcpFrame * (0.5 + subpix_shift));
    }
