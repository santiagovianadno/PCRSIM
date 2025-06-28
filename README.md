# PCRSIM

Visualizador interactivo del proceso de PCR con detección de manos. Requiere Python 3.10, OpenGL y una webcam.

## Instalación rápida
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# o source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

## Ejecución
```bash
python basteria_mediapipe.py
# Windows (si has añadido Python 3.10 al launcher)
py -3.10 basteria_mediapipe.py
```

## Controles de teclado
| Tecla | Función |
|-------|---------|
| C | Mostrar/ocultar ventana de cámara |
| H | Activar/desactivar control de manos |
| A | Ciclar velocidad de rotación automática |
| R | Reiniciar posición de cámara |
| F | Pantalla completa |
| Ratón botón izq. | Rotar modelo |
| Rueda ratón | Zoom |
| ESC | Salir |

## Gestos de mano
| Etapa | Mano | Gesto | Efecto |
|-------|------|-------|--------|
| Todas | Derecha | Palma en movimiento | Rotar escena |
| Todas | Derecha | Pinch | Zoom |
| 1 (Bacteria) | Izquierda | Pinch cerrado | Vibración, color rojo, transparencia |
| 1 | Izquierda | Pinch abierto | Estado normal |
| 2 (ADN) | Izquierda | Pinch | Separar/unir hebras de ADN |
| 3 (Enzima) | Izquierda | Pinch | Acercar/alejar polimerasa al ADN |
| 4 (PCR) | Izquierda | Pinch cerrado | Centrifugado (rotación rápida) |
| 4 | Izquierda | Movimiento | Generar fragmentos de ADN |
| Todas | Ambas | Índice derecho toca palma izquierda | Cambiar de etapa |

## Modelos utilizados
Los archivos `.ply` se encuentran en `models/`.

## Dependencias principales
- opencv-python
- mediapipe
- pygame
- numpy
- PyOpenGL
- plyfile

Las dependencias opcionales aparecen comentadas en `requirements.txt`.
