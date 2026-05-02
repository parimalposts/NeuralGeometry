// Neural Geometry — fragment shader (toggled with F1)
// Applies a 5-stop heatmap: black → blue → cyan → orange → white
#version 120

uniform sampler2D p3d_Texture0;

varying vec4 v_color;
varying vec2 v_uv;
varying float v_intensity;

vec3 heatmap(float t) {
    // 5 stops at t = 0.0, 0.25, 0.5, 0.75, 1.0
    vec3 c0 = vec3(0.05, 0.05, 0.1);
    vec3 c1 = vec3(0.1,  0.3,  0.9);
    vec3 c2 = vec3(0.1,  0.9,  0.9);
    vec3 c3 = vec3(1.0,  0.4,  0.1);
    vec3 c4 = vec3(1.0,  1.0,  1.0);

    if (t < 0.25) return mix(c0, c1, t / 0.25);
    if (t < 0.5)  return mix(c1, c2, (t - 0.25) / 0.25);
    if (t < 0.75) return mix(c2, c3, (t - 0.5)  / 0.25);
    return mix(c3, c4, (t - 0.75) / 0.25);
}

void main() {
    vec4 tex = texture2D(p3d_Texture0, v_uv);
    float intensity = clamp(v_color.r * 0.6 + v_color.b * 0.2, 0.0, 1.0);
    vec3 heat = heatmap(intensity);
    vec3 final_color = mix(heat, tex.rgb, 0.4);
    gl_FragColor = vec4(final_color, 1.0);
}
