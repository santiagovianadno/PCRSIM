# PCRSIM

Proyecto académico desarrollado para el curso "Desafíos en las Ciencias Biológicas y el Diseño, BIO356D-1". Este sistema de videomapping interactivo simula el proceso de PCR (Reacción en Cadena de la Polimerasa) usando células termófilas como protagonistas.

## Controles

| Acción | Tecla / Acción |
|--------|----------------|
| Interactuar con células | Mouse (versión simple) / Manos (versión completa) |
| Siguiente etapa PCR | `ESPACIO` |
| Reiniciar simulación | `R` |
| Pausar / Reanudar | `P` |
| Rotar cámara | Arrastrar mouse |
| Zoom | Rueda del mouse |
| Salir | `ESC` |

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

Ejecuta la simulación simple (sin cámara web):

```bash
python pcr_simple_simulation.py
```

Ejecuta la versión completa con interacción de manos (requiere cámara web):

```bash
python pcr_advanced_simulation.py
```
