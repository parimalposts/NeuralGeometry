shader_type spatial;
render_mode vertex_lighting, cull_back;

uniform sampler2D activation_texture : source_color, hint_default_white;
uniform float emission_strength : hint_range(0.0, 1.0) = 0.25;

void vertex() {
    // Vertex colors drive emissive glow intensity
    // COLOR is set per-vertex by neural_sphere.gd
}

void fragment() {
    vec4 tex_sample = texture(activation_texture, UV);
    vec3 vert_color = COLOR.rgb;

    // Blend vertex color (neural heatmap) with activation texture
    ALBEDO = mix(vert_color, tex_sample.rgb, 0.45);

    // Low-frequency emission from vertex color
    EMISSION = vert_color * emission_strength;

    ROUGHNESS = 0.55;
    METALLIC  = 0.2;
    SPECULAR  = 0.5;
}
