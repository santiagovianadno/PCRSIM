# PCR Termophilic Cells Interactive Videomapping

Sistema de videomapping interactivo que simula el proceso de PCR (Reacción en Cadena de la Polimerasa) usando células termófilas como protagonistas. Este proyecto combina biología molecular, arte digital e interactividad para crear una experiencia educativa y artística única.

## 🧬 Concepto

El proyecto explora la historia revolucionaria del PCR a través de las células termófilas que hicieron posible esta técnica:

- **Thermus aquaticus**: Descubierta en Yellowstone, proporcionó la Taq polimerasa
- **Pyrococcus furiosus**: Extremófila que soporta temperaturas de hasta 105°C
- **Thermococcus litoralis**: Bacteria marina termófila

## 🎮 Controles

| Acción | Control |
|--------|---------|
| **Interactuar con células** | Mover mouse (versión simple) / Manos (versión completa) |
| **Siguiente etapa PCR** | `ESPACIO` |
| **Reiniciar simulación** | `R` |
| **Pausar/Reanudar** | `P` |
| **Rotar cámara** | Arrastrar mouse |
| **Zoom** | Scroll del mouse |
| **Salir** | `ESC` |

## 🔬 Etapas del PCR Simuladas

### 1. **Desnaturalización** (94°C)
- Separación de las cadenas de DNA
- Células cambian a color rojo intenso
- Efectos de calor extremo

### 2. **Annealing** (50-65°C)
- Unión de primers al DNA
- Células en color naranja
- Visualización de primers

### 3. **Extensión** (72°C)
- Síntesis de nueva cadena de DNA
- Células en color amarillo
- Efectos de síntesis

### 4. **Enfriamiento** (25°C)
- Preparación para el siguiente ciclo
- Células regresan a color verde
- Recuperación de energía

## 🛠️ Instalación

### Requisitos
- Python 3.8+ (recomendado 3.11 para versión completa)
- Cámara web (opcional para versión simple)
- Windows/macOS/Linux
- OpenGL compatible

### Pasos

1. **Clonar proyecto**
```bash
git clone [tu-repositorio]
cd VideomappingART02
```

2. **Instalación automática**
```bash
python setup.py
```

3. **Instalación manual (si setup.py falla)**
```bash
pip install pygame numpy pyopengl plyfile scipy matplotlib pillow
```

4. **Ejecutar simulación**

   **Versión Simple (compatible con Python 3.13):**
   ```bash
   python pcr_simple_simulation.py
   ```

   **Versión Completa (requiere Python 3.11 o anterior):**
   ```bash
   python pcr_thermophilic_simulation.py
   python pcr_advanced_simulation.py
   ```

## 🎥 Uso

### Versión Simple (Recomendada para Python 3.13)
1. **Inicia el programa** - `python pcr_simple_simulation.py`
2. **Mueve el mouse** para interactuar con las células
3. **Presiona ESPACIO** para avanzar manualmente entre etapas
4. **Observa** cómo las células responden a los cambios de temperatura

### Versión Completa (Python 3.11 o anterior)
1. **Inicia el programa** - La cámara se activa automáticamente
2. **Muestra tus manos** a la cámara para interactuar con las células
3. **Presiona ESPACIO** para avanzar manualmente entre etapas
4. **Observa** cómo las células responden a los cambios de temperatura
5. **Experimenta** con diferentes gestos de manos

## 🔧 Características Técnicas

### Interactividad
- **Versión Simple**: Interacción con mouse
- **Versión Completa**: MediaPipe Hand Tracking para detección de manos
- **Gestos interactivos**: Tocar, mover y activar células
- **Respuesta visual**: Las células reaccionan a la interacción

### Visualización 3D
- **OpenGL**: Renderizado 3D avanzado
- **PLY Models**: Soporte para modelos 3D de células
- **Efectos de partículas**: Energía y calor visual
- **Animaciones fluidas**: Transiciones suaves entre etapas

### Simulación Biológica
- **Temperatura realista**: Simulación precisa de rangos de PCR
- **Células termófilas**: Diferentes tipos con características únicas
- **Ciclos de PCR**: Reproducción del proceso completo
- **Efectos de energía**: Consumo y regeneración de energía celular

## 📁 Estructura del Proyecto

```
VideomappingART02/
├── pcr_simple_simulation.py      # Simulación simple (Python 3.13+)
├── pcr_thermophilic_simulation.py # Simulación básica completa
├── pcr_advanced_simulation.py    # Simulación avanzada completa
├── ply_cell_renderer.py          # Renderizador PLY especializado
├── models/
│   └── thermophilic_cell.ply     # Modelo 3D de célula
├── requirements.txt              # Dependencias
├── setup.py                     # Script de instalación
├── example_usage.py             # Ejemplo de uso
├── TECHNICAL_DOCS.md            # Documentación técnica
└── README.md                    # Documentación principal
```

## 🧪 Tipos de Células Termófilas

### Thermus aquaticus
- **Temperatura óptima**: 70°C
- **Temperatura máxima**: 80°C
- **Color**: Naranja
- **Historia**: Descubierta en Yellowstone, clave para el desarrollo del PCR

### Pyrococcus furiosus
- **Temperatura óptima**: 100°C
- **Temperatura máxima**: 105°C
- **Color**: Rojo intenso
- **Característica**: Extremófila hipertermófila

### Thermococcus litoralis
- **Temperatura óptima**: 88°C
- **Temperatura máxima**: 98°C
- **Color**: Verde-amarillo
- **Hábitat**: Marino

## 🎨 Efectos Visuales

- **Cambio de color por temperatura**: Verde → Amarillo → Naranja → Rojo
- **Partículas de energía**: Efectos de brillo y movimiento
- **Distorsión por calor**: Efectos visuales en altas temperaturas
- **Animación de DNA**: Visualización de hebras durante el proceso
- **Efectos de glow**: Brillo intenso en células activas

## 🔬 Aplicaciones Educativas

Este proyecto puede utilizarse para:

- **Educación en biología molecular**: Visualización del PCR
- **Historia de la ciencia**: Importancia de las células termófilas
- **Arte digital interactivo**: Experiencias inmersivas
- **Investigación**: Simulación de procesos biológicos

## 🚀 Futuras Mejoras

- [ ] Más tipos de células termófilas
- [ ] Efectos de sonido ambientales
- [ ] Modo multijugador
- [ ] Exportación de datos de simulación
- [ ] Integración con microscopios digitales
- [ ] Realidad virtual (VR)
- [ ] Soporte completo para Python 3.13 con MediaPipe

## 📚 Referencias

- **PCR History**: Kary Mullis y el desarrollo de la técnica
- **Thermus aquaticus**: Descubrimiento en Yellowstone
- **Extremófilos**: Organismos que viven en condiciones extremas
- **Biología molecular**: Fundamentos del PCR

## ⚠️ Notas de Compatibilidad

- **Python 3.13**: Usar `pcr_simple_simulation.py` (sin MediaPipe)
- **Python 3.11 o anterior**: Usar versiones completas con MediaPipe
- **MediaPipe**: No compatible con Python 3.13, usar versión simple

---

*Desarrollado para explorar la intersección entre arte digital, biología molecular e interactividad humana.*
