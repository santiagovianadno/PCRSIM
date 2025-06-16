#version 330 core

// Inputs del vertex shader
in vec2 v_texcoord;
in vec2 v_position;

// Output del fragment shader
out vec4 fragColor;

// Uniforms (par�metros del shader)
uniform float u_time;           // Tiempo en segundos
uniform vec2 u_resolution;      // Resoluci�n de la pantalla
uniform vec2 u_hand_pos;        // Posici�n de la mano (0-1)
uniform float u_hand_detected;  // 1.0 si hay mano detectada, 0.0 si no
uniform float u_intensity;      // Intensidad del efecto (0-1)

// Par�metros del efecto CUERPO-R�O
const float FLOW_DENSITY = 40.0;        // Densidad de flujos de agua
const float FLOW_SPEED = 1.5;           // Velocidad lenta y org�nica
const float TURBULENCE = 2.0;           // Turbulencia del agua
const float MAX_DISPLACEMENT = 0.4;     // Desplazamiento fluido
const float INTERACTION_RADIUS = 0.8;   // Radio amplio como cuenca
const float FLOW_WIDTH = 0.4;           // Grosor de flujos org�nicos

// Funci�n para simular flujo org�nico de agua/cuerpo
float calculateWaterFlow(vec2 pos, vec2 sourcePos, float time) {
    // Distancia desde el punto de interacci�n (fuente del r�o)
    float distanceToSource = length(pos - sourcePos);
    
    // El r�o fluye hacia abajo (en Y) con meandros naturales
    float flowDirection = pos.y - sourcePos.y;
    
    // Solo fluir hacia abajo desde la fuente
    if (flowDirection < 0.0 || distanceToSource > INTERACTION_RADIUS) {
        return 0.0;
    }
    
    // Influencia basada en distancia (como cuenca hidrogr�fica)
    float influence = 1.0 - (distanceToSource / INTERACTION_RADIUS);
    influence = smoothstep(0.0, 1.0, influence);
    
    // Meandros naturales del r�o (movimiento sinuoso)
    float meanderX = sin(pos.y * 4.0 + time * FLOW_SPEED) * 0.1;
    float meanderY = sin(pos.y * 6.0 + time * FLOW_SPEED * 0.7) * 0.05;
    
    // Turbulencia del agua
    float turbulence1 = sin(pos.x * 8.0 + pos.y * 3.0 - time * FLOW_SPEED) * 0.05;
    float turbulence2 = sin(pos.x * 12.0 + pos.y * 5.0 - time * FLOW_SPEED * 1.3) * 0.03;
    
    // Flujo gravitacional hacia abajo
    float gravity_flow = flowDirection * 0.2;
    
    // Combinaci�n de movimientos org�nicos
    float displacement = (meanderX + meanderY + turbulence1 + turbulence2 + gravity_flow) * influence;
    
    return displacement * MAX_DISPLACEMENT * u_intensity;
}

// Funci�n para generar m�ltiples flujos como afluentes
float calculateMultipleFlows(vec2 pos, vec2 sourcePos, float time) {
    float displacement = 0.0;
    
    // Flujo principal
    displacement += calculateWaterFlow(pos, sourcePos, time);
    
    // Afluentes con diferentes velocidades
    displacement += calculateWaterFlow(pos, sourcePos, time * 1.2) * 0.6;
    displacement += calculateWaterFlow(pos, sourcePos, time * 0.8) * 0.4;
    
    // Flujo profundo m�s lento
    displacement += calculateWaterFlow(pos, sourcePos, time * 0.4) * 0.8;
    
    return displacement;
}

float generateFlowingLines(vec2 pos, vec2 sourcePos, float time) {
    float displacement = 0.0;
    
    if (u_hand_detected > 0.5) {
        displacement = calculateMultipleFlows(pos, sourcePos, time);
    } else {
        // Flujo constante sutil (el r�o siempre fluye)
        displacement = sin(pos.y * 4.0 + time * FLOW_SPEED) * 0.02;
        displacement += sin(pos.x * 6.0 + time * FLOW_SPEED * 0.7) * 0.01;
    }
    
    // Aplicar desplazamiento a la posici�n X (flujo horizontal)
    float adjustedX = pos.x + displacement;
    
    // Generar l�neas de flujo org�nicas
    float flowPattern = adjustedX * FLOW_DENSITY;
    float flowValue = abs(fract(flowPattern) - 0.5) * 2.0;
    
    // Suavizar para efecto org�nico
    float flow = smoothstep(1.0 - FLOW_WIDTH, 1.0, flowValue);
    
    return 1.0 - flow;
}

void main() {
    vec2 uv = v_texcoord;
    vec2 pos = uv;
    pos.x *= u_resolution.x / u_resolution.y;
    
    vec2 sourcePos = u_hand_pos;
    sourcePos.x *= u_resolution.x / u_resolution.y;
    
    // Fondo negro como noche del r�o
    vec3 backgroundColor = vec3(0.0, 0.0, 0.0);
    
    float flows = generateFlowingLines(pos, sourcePos, u_time);
    
    // Color azul-verdoso del agua del Mapocho
    vec3 waterColor = vec3(0.2, 0.6, 0.8);
    
    // Variaci�n seg�n profundidad (posici�n Y)
    waterColor.r += sin(pos.y * 2.0 + u_time * 0.5) * 0.1;
    waterColor.g += sin(pos.y * 3.0 + u_time * 0.3) * 0.15;
    waterColor.b += sin(pos.y * 4.0 + u_time * 0.7) * 0.2;
    
    // Mezclar agua con fondo
    vec3 finalColor = mix(backgroundColor, waterColor, flows);
    
    // Agregar reflexi�n sutil de la ciudad
    float reflection = sin(pos.x * 20.0 + u_time * 2.0) * 0.05;
    finalColor += vec3(reflection * 0.3, reflection * 0.3, reflection * 0.1);
    
    fragColor = vec4(finalColor, 1.0);
}
