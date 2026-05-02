// Neural Geometry — vertex shader (toggled with F1)
#version 120

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

attribute vec4 p3d_Vertex;
attribute vec3 p3d_Normal;
attribute vec4 p3d_Color;
attribute vec2 p3d_MultiTexCoord0;

varying vec4 v_color;
varying vec2 v_uv;
varying float v_intensity;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    v_color = p3d_Color;
    v_uv = p3d_MultiTexCoord0;
    // intensity = displacement magnitude encoded in alpha
    v_intensity = p3d_Color.a;
}
