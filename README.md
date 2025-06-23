# PCRSIM

Proyecto académico desarrollado para el curso "Desafíos en las Ciencias Biológicas y el Diseño, BIO356D-1". Este sistema de videomapping interactivo simula el proceso de PCR (Reacción en Cadena de la Polimerasa) usando células termófilas como protagonistas.

## Controles

| Acción | Tecla / Acción |
|--------|----------------|
| Interactuar con células | Manos |
| Mostrar/Ocultar ventana de cámara | `C` |
| Activar/Desactivar control de manos | `H` |
| Cambiar velocidad rotación automática | `A` |
| Reiniciar posición de cámara | `R` |
| Rotar cámara | Arrastrar mouse |
| Zoom | Rueda del mouse |
| Salir | `ESC` |

## Gestos

 MANO DERECHA:
    Mover palma = Rotar modelo
    Pinch = Controlar zoom

 MANO IZQUIERDA:
   (Etapa 1)  Juntar dedos = VIBRACIÓN + ROJO + TRANSPARENCIA
   (Etapa 1)  Separar dedos = NORMAL + BLANCO + OPACO
   (Etapa 3)  Juntar dedos = Separar/Unir Polimerasa

 GESTOS ADICIONALES:
   (Todos los modos)  Toca tu palma izquierda con el índice derecho para ciclar de nivel
   (Etapa 2)  Manos separadas/juntas = Separar/Unir hebras de ADN
   (Etapa 4)  Mueve la mano izquierda para replicar fragmentos de ADN

## Instalación (Python 3.10)

Requisitos previos:
- Python 3.10
- Tarjeta gráfica compatible con OpenGL

Pasos recomendados:

```bash
# 1. Clona el repositorio
git clone https://github.com/<TU-USUARIO>/PCRSIM.git
cd PCRSIM

# 2. Crea y activa un entorno virtual (opcional pero recomendado)
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt
```

Ejecuta la simulación

py -3.10 basteria_mediapipe.py
