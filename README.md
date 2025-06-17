# VideomappingART - Ríos Interactivos

Sistema de videomapping interactivo con detección de movimiento que contrasta dos paradigmas fluviales desde una perspectiva posthumanista y ecológica.

Exploración artística e investigativa de las agencias humanas/más-que-humanas en paisajes del Antropoceno, contrastando:

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
- Python 3.10
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

## 🔧 Dependencias

- **opencv-python**: Procesamiento de imagen y cámara
- **mediapipe**: Detección de manos en tiempo real
- **pygame**: Motor de gráficos y renderizado
- **numpy**: Operaciones matemáticas
