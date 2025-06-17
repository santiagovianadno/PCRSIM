#version 330 core

// Atributos del vértice
in vec2 in_position;
in vec2 in_texcoord;

// Outputs al fragment shader
out vec2 v_texcoord;
out vec2 v_position;

void main() {
    // Pasar coordenadas de textura al fragment shader
    v_texcoord = in_texcoord;
    v_position = in_position;
    
    // Posición del vértice en coordenadas de clip
    gl_Position = vec4(in_position, 0.0, 1.0);
} 