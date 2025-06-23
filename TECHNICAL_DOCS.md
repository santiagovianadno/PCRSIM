# Documentación Técnica - PCR Termophilic Cells Interactive

## 🏗️ Arquitectura del Sistema

### Componentes Principales

#### 1. **PCRSimulation** (`pcr_thermophilic_simulation.py`)
- **Propósito**: Simulación básica del proceso de PCR
- **Responsabilidades**:
  - Gestión del ciclo de vida de la aplicación
  - Coordinación entre MediaPipe y OpenGL
  - Manejo de eventos de pygame
  - Renderizado básico de células

#### 2. **AdvancedPCRSimulation** (`pcr_advanced_simulation.py`)
- **Propósito**: Versión avanzada con características adicionales
- **Características**:
  - Células con física avanzada
  - Sistema de división celular
  - Efectos visuales mejorados
  - Estadísticas en tiempo real

#### 3. **ThermophilicCellRenderer** (`ply_cell_renderer.py`)
- **Propósito**: Renderizado especializado de células 3D
- **Funcionalidades**:
  - Carga y renderizado de modelos PLY
  - Efectos de partículas
  - Visualización de DNA
  - Efectos de temperatura

#### 4. **PLYCellModel** (`ply_cell_renderer.py`)
- **Propósito**: Manejo de modelos 3D en formato PLY
- **Características**:
  - Carga automática de geometría
  - Fallback a geometría por defecto
  - Optimización de renderizado

## 🔧 Implementación Técnica

### Detección de Manos (MediaPipe)

```python
# Configuración de MediaPipe
self.hands = mp_hands.Hands(
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=2
)

# Procesamiento de landmarks
palm = hand_landmarks.landmark[9]  # Punto central de la palma
x = (palm.x - 0.5) * 16  # Escalar a coordenadas 3D
y = (0.5 - palm.y) * 8
z = palm.z * 10
```

### Renderizado 3D (OpenGL)

```python
# Configuración de OpenGL
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Renderizado de vértices
glEnableClientState(GL_VERTEX_ARRAY)
glVertexPointer(3, GL_FLOAT, 0, vertices)
glDrawArrays(GL_POINTS, 0, len(vertices))
```

### Simulación de Temperatura

```python
def update_temperature(self, dt: float, pcr_stage: str):
    target_temp = PCRStage.get_temperature(pcr_stage)
    temp_diff = target_temp - self.temperature
    self.temperature += temp_diff * dt * 2.0  # Transición suave
```

## 📊 Estructura de Datos

### Célula Termófila

```python
class ThermophilicCell:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
        self.temperature = 25.0
        self.energy = 100.0
        self.active = True
        self.color = (0.2, 0.8, 0.2)
        self.size = random.uniform(0.5, 1.5)
```

### Etapas de PCR

```python
class PCRStage:
    DENATURATION = "denaturation"  # 94°C
    ANNEALING = "annealing"        # 50-65°C
    EXTENSION = "extension"        # 72°C
    COOLING = "cooling"           # 25°C
```

## 🎨 Efectos Visuales

### Sistema de Partículas

```python
def create_energy_particle(self, position, velocity, color, lifetime):
    return {
        'position': position.copy(),
        'velocity': velocity.copy(),
        'color': color,
        'lifetime': lifetime,
        'max_lifetime': lifetime,
        'size': random.uniform(0.1, 0.3)
    }
```

### Cambio de Color por Temperatura

```python
def get_color(self) -> Tuple[float, float, float]:
    if self.temperature > 80:
        return (0.8, 0.2, 0.2)  # Rojo
    elif self.temperature > 60:
        return (0.8, 0.6, 0.2)  # Naranja
    elif self.temperature > 40:
        return (0.8, 0.8, 0.2)  # Amarillo
    else:
        return (0.2, 0.8, 0.2)  # Verde
```

## 🔄 Flujo de Datos

### 1. Captura de Video
```
Cámara → OpenCV → MediaPipe → Landmarks de Manos
```

### 2. Procesamiento de Interacción
```
Landmarks → Coordenadas 3D → Influencia en Células
```

### 3. Simulación Biológica
```
Estado PCR → Temperatura Objetivo → Cambio en Células
```

### 4. Renderizado
```
Células + Efectos → OpenGL → Pantalla
```

## ⚡ Optimizaciones

### 1. **Renderizado Eficiente**
- Uso de `glDrawArrays` para puntos
- `glDrawElements` para modelos complejos
- Vertex arrays para mejor rendimiento

### 2. **Gestión de Memoria**
- Reutilización de objetos de partículas
- Limpieza automática de partículas muertas
- Carga lazy de modelos PLY

### 3. **Detección de Manos**
- Configuración optimizada de MediaPipe
- Procesamiento solo cuando es necesario
- Cache de resultados

## 🐛 Manejo de Errores

### 1. **Cámara No Disponible**
```python
try:
    self.cap = cv2.VideoCapture(0)
    if not self.cap.isOpened():
        raise Exception("No se pudo acceder a la cámara")
except Exception as e:
    print(f"Error de cámara: {e}")
    # Continuar sin cámara
```

### 2. **Modelo PLY No Encontrado**
```python
try:
    self.load_ply_model("default", "models/thermophilic_cell.ply")
except:
    print("Modelo PLY no encontrado, usando geometría por defecto")
    self.create_default_geometry()
```

### 3. **OpenGL No Disponible**
```python
try:
    pygame.display.set_mode((width, height), pygame.OPENGL)
except pygame.error:
    print("OpenGL no disponible")
    sys.exit(1)
```

## 📈 Métricas de Rendimiento

### Objetivos de Rendimiento
- **FPS**: 60 FPS constante
- **Latencia**: < 100ms para interacción de manos
- **Memoria**: < 500MB RAM
- **CPU**: < 30% uso promedio

### Monitoreo
```python
# Estadísticas en tiempo real
self.stats = {
    'total_cells': len(self.cells),
    'active_cells': sum(1 for c in self.cells if c.active),
    'avg_temperature': sum(c.temperature for c in self.cells) / len(self.cells),
    'fps': clock.get_fps()
}
```

## 🔧 Configuración

### Archivo `config.ini`
```ini
[Display]
width = 1280
height = 720
fullscreen = false

[Camera]
device = 0
width = 640
height = 480

[PCR]
auto_advance = true
cycle_duration = 3.0
max_cycles = 30
```

## 🧪 Testing

### Pruebas Unitarias
```python
def test_cell_temperature_update():
    cell = ThermophilicCell(0, 0, 0)
    cell.update(1.0, PCRStage.DENATURATION, [])
    assert cell.temperature > 25.0

def test_hand_interaction():
    cell = ThermophilicCell(0, 0, 0)
    hand_pos = (1.0, 0.0, 0.0)
    cell.handle_hand_interaction([hand_pos], 1.0)
    assert cell.energy > 100.0
```

### Pruebas de Integración
```python
def test_full_simulation():
    simulation = PCRSimulation()
    simulation.update(1.0)
    assert len(simulation.cells) > 0
    assert simulation.current_stage in PCRStage.__dict__.values()
```

## 🚀 Escalabilidad

### Posibles Mejoras
1. **Multithreading**: Separar captura de video y renderizado
2. **GPU Computing**: Usar CUDA/OpenCL para partículas
3. **Redes Neuronales**: Mejorar detección de gestos
4. **Realidad Virtual**: Soporte para VR/AR
5. **Multijugador**: Interacción colaborativa

### Arquitectura Modular
```
Core/
├── Simulation/
│   ├── PCREngine.py
│   ├── CellManager.py
│   └── PhysicsEngine.py
├── Rendering/
│   ├── OpenGLRenderer.py
│   ├── ParticleSystem.py
│   └── PLYLoader.py
├── Interaction/
│   ├── HandTracker.py
│   ├── GestureRecognizer.py
│   └── InputManager.py
└── Utils/
    ├── ConfigManager.py
    ├── Logger.py
    └── MathUtils.py
```

## 📚 Referencias Técnicas

### Bibliotecas Utilizadas
- **MediaPipe**: Detección de manos en tiempo real
- **OpenGL**: Renderizado 3D acelerado por hardware
- **Pygame**: Gestión de ventanas y eventos
- **OpenCV**: Procesamiento de video
- **NumPy**: Operaciones matemáticas vectorizadas
- **PLYFile**: Carga de modelos 3D

### Estándares
- **PLY Format**: Stanford Triangle Format
- **OpenGL 3.3+**: Shader-based rendering
- **MediaPipe 0.10+**: Hand tracking API

---

*Documentación técnica actualizada para la versión 1.0 del proyecto* 