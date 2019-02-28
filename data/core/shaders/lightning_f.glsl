//GLSL
#version 130
in float mutant;
in float factor;

void main()
    {
    vec3 color=mix(vec3(0.2+mutant*1.5, 0.1+mutant, 0.9), vec3(1.0-mutant, 1.0-mutant, 1.0), (factor-0.2)*3.0);
    //vec3 color=vec3(1.0, 1.0, 1.0);
    gl_FragData[0]=vec4(color, clamp(0.5+factor*2.0, 0.5, 1.0));
    gl_FragData[1]=vec4(0.0, 0.5, 1.0, 0.0);
    }
