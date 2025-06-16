# VideomappingART - Ríos Interactivos

Sistema de videomapping interactivo con detección de movimiento que contrasta dos paradigmas fluviales desde una perspectiva posthumanista y ecológica.

## Concepto

Exploración artística e investigativa de las agencias humanas/más-que-humanas en paisajes del Antropoceno, contrastando:

- **MAPOCHO CANALIZADO**: Río urbano constricto - respuesta dramática a la interacción
- **MAIPO ABIERTO**: Río natural libre - movimiento sutil y orgánico

## Funcionalidades

- Detección de movimiento con cámara web (OpenCV)
- Interacción fluida sin artefactos visuales  
- Sistema de aleatoriedad orgánica multicapa
- Resolución Full HD 1920x1080
- Contraste conceptual posthumanista
- Rendimiento en tiempo real a 60 FPS

## Controles

| Acción | Control |
|--------|---------|
| **Manipular agua** | Movimiento en cámara |
| **Cambiar río** | `ESPACIO` |
| **Activar/desactivar cámara** | `C` |
| **Pantalla completa** | `F11` |
| **Salir** | `ESC` |

## Instalación

### Requisitos
- Python 3.8+
- Cámara web
- Windows/macOS/Linux

### Pasos

1. **Clonar proyecto**
```bash
git clone [tu-repositorio]
cd VideomappingART02
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Ejecutar videomapping**
```bash
python videomapping_final.py
```

## 🎥 Uso

1. **Inicia el programa** - La cámara se activa automáticamente
2. **Muestra tus manos** a la cámara para interactuar
3. **Presiona ESPACIO** para alternar entre ríos
4. **Experimenta** las diferentes respuestas de cada paradigma

### Debug de Cámara
- Se abre una ventana adicional mostrando la detección de manos
- Puntos rojos marcan las articulaciones detectadas
- Si no detecta manos, usa el mouse como fallback

## 🏛️ Contexto Académico

**Proyecto de investigación universitaria**
- **Tema**: Agencias humanas/más-que-humanas en el Antropoceno
- **Enfoque**: Posthumanismo ecológico
- **Caso de estudio**: Ríos de Santiago (Mapocho urbano vs Maipo natural)
- **Metodología**: Videomapping interactivo como herramienta de investigación

## 📁 Estructura del Proyecto

```
VideomappingART02/
├── videomapping_final.py    # 🚀 Aplicación principal
├── requirements.txt         # 📦 Dependencias
└── README.md               # 📖 Documentación
```

## 🔧 Dependencias

- **opencv-python**: Procesamiento de imagen y cámara
- **mediapipe**: Detección de manos en tiempo real
- **pygame**: Motor de gráficos y renderizado
- **numpy**: Operaciones matemáticas

## 🎨 Características Técnicas

### Mapocho Canalizado
- Canal de concreto estrecho (180px)
- 8 líneas horizontales de agua
- Ondulación dramática (80px amplitud)
- Respuesta intensa a la presencia humana

### Maipo Abierto  
- Lecho amplio y natural
- 5 brazos con grosores variables [6, 18, 3, 25, 12]
- Movimiento sutil vertical
- Múltiples capas de aleatoriedad orgánica

### Sistema de Detección
- MediaPipe Hands con 21 puntos de seguimiento
- Mapeo de coordenadas cámara → pantalla
- Procesamiento en hilo separado para 60 FPS
- Fallback automático a mouse

## 🐛 Solución de Problemas

**Cámara no detecta:**
- Verifica que no esté siendo usada por otra aplicación
- Presiona `C` para reiniciar la cámara
- Asegúrate de tener buena iluminación

**Rendimiento lento:**
- Cierra otras aplicaciones pesadas
- Reduce la resolución de la cámara si es necesario

**Manos no detectadas:**
- Mantén las manos bien iluminadas
- Evita fondos complejos
- Muestra las palmas hacia la cámara

## 📄 Licencia

Proyecto académico de investigación - Universidad de Santiago

---

*"Exploring the fluid boundaries between human and more-than-human agencies in Anthropocene landscapes through interactive videomapping."* 