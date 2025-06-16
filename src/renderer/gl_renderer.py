import moderngl
import numpy as np
import pygame
import time
from pathlib import Path
from typing import Tuple, Optional
from ..utils.math_utils import smooth_value


class GLRenderer:
    """Renderer OpenGL para efectos de videomapping interactivo."""
    
    def __init__(self, width: int = 1280, height: int = 720, fullscreen: bool = False):
        """
        Inicializa el renderer OpenGL.
        
        Args:
            width: Ancho de la ventana
            height: Alto de la ventana
            fullscreen: Si mostrar en pantalla completa
        """
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        
        # Estado del renderer
        self.ctx = None
        self.program = None
        self.vao = None
        self.screen = None
        self.clock = None
        
        # Parámetros del shader
        self.start_time = time.time()
        self.hand_pos = (0.5, 0.5)  # Posición de la mano (normalizada)
        self.hand_detected = 0.0    # Si hay mano detectada
        self.intensity = 1.0        # Intensidad del efecto
        
        # Suavizado de valores
        self.smooth_hand_pos = [0.5, 0.5]
        self.smooth_hand_detected = 0.0
        
        # Rutas de shaders
        shader_dir = Path(__file__).parent.parent / "shaders"
        self.vertex_shader_path = shader_dir / "vertex_shader.glsl"
        self.fragment_shader_path = shader_dir / "fragment_shader.glsl"
        
    def initialize(self) -> bool:
        """
        Inicializa Pygame y OpenGL.
        
        Returns:
            True si se inicializó correctamente, False si no
        """
        try:
            # Inicializar Pygame
            pygame.init()
            
            # Configurar OpenGL
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, 
                                          pygame.GL_CONTEXT_PROFILE_CORE)
            
            # Crear ventana
            flags = pygame.OPENGL | pygame.DOUBLEBUF
            if self.fullscreen:
                flags |= pygame.FULLSCREEN
                
            self.screen = pygame.display.set_mode((self.width, self.height), flags)
            pygame.display.set_caption("Videomapping Interactivo - Ondas")
            
            # Crear contexto ModernGL
            self.ctx = moderngl.create_context()
            
            # Configurar viewport
            self.ctx.viewport = (0, 0, self.width, self.height)
            
            # Cargar y compilar shaders
            if not self._load_shaders():
                return False
            
            # Crear geometría (quad completo)
            self._create_quad()
            
            # Crear reloj para FPS
            self.clock = pygame.time.Clock()
            
            print(f"Renderer inicializado: {self.width}x{self.height}")
            print(f"OpenGL Version: {self.ctx.info['GL_VERSION']}")
            return True
            
        except Exception as e:
            print(f"Error inicializando renderer: {e}")
            return False
    
    def _load_shaders(self) -> bool:
        """
        Carga y compila los shaders.
        
        Returns:
            True si se cargaron correctamente, False si no
        """
        try:
            # Leer vertex shader
            with open(self.vertex_shader_path, 'r') as f:
                vertex_shader = f.read()
            
            # Leer fragment shader
            with open(self.fragment_shader_path, 'r') as f:
                fragment_shader = f.read()
            
            # Compilar programa de shaders
            self.program = self.ctx.program(
                vertex_shader=vertex_shader,
                fragment_shader=fragment_shader
            )
            
            print("Shaders compilados correctamente")
            return True
            
        except Exception as e:
            print(f"Error cargando shaders: {e}")
            return False
    
    def _create_quad(self):
        """Crea un quad que cubre toda la pantalla."""
        # Vértices del quad (posición y coordenadas de textura)
        vertices = np.array([
            # Posición (x, y)    # Texcoords (u, v)
            -1.0, -1.0,          0.0, 0.0,
             1.0, -1.0,          1.0, 0.0,
             1.0,  1.0,          1.0, 1.0,
            -1.0,  1.0,          0.0, 1.0
        ], dtype=np.float32)
        
        # Índices para dos triángulos que forman el quad
        indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)
        
        # Crear buffers
        vbo = self.ctx.buffer(vertices.tobytes())
        ibo = self.ctx.buffer(indices.tobytes())
        
        # Crear VAO
        self.vao = self.ctx.vertex_array(
            self.program, 
            [(vbo, '2f 2f', 'in_position', 'in_texcoord')],
            ibo
        )
        
    def update_hand_position(self, x: float, y: float, detected: bool = True):
        """
        Actualiza la posición de la mano.
        
        Args:
            x, y: Coordenadas normalizadas de la mano (0-1)
            detected: Si la mano está siendo detectada
        """
        # Suavizar la posición de la mano
        smoothing = 0.15
        self.smooth_hand_pos[0] = smooth_value(self.smooth_hand_pos[0], x, smoothing)
        self.smooth_hand_pos[1] = smooth_value(self.smooth_hand_pos[1], y, smoothing)
        
        # Suavizar el estado de detección
        target_detected = 1.0 if detected else 0.0
        self.smooth_hand_detected = smooth_value(self.smooth_hand_detected, target_detected, 0.1)
        
        self.hand_pos = (self.smooth_hand_pos[0], self.smooth_hand_pos[1])
        self.hand_detected = self.smooth_hand_detected
    
    def set_intensity(self, intensity: float):
        """
        Establece la intensidad del efecto.
        
        Args:
            intensity: Intensidad (0-1)
        """
        self.intensity = max(0.0, min(1.0, intensity))
    
    def render(self) -> bool:
        """
        Renderiza un frame.
        
        Returns:
            True si debe continuar, False si se debe salir
        """
        # Manejar eventos de Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_F:
                    # Toggle fullscreen
                    self._toggle_fullscreen()
        
        # Limpiar pantalla
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # Actualizar uniforms del shader
        current_time = time.time() - self.start_time
        
        if self.program:
            # Tiempo
            self.program['u_time'].value = float(current_time)
            
            # Resolución
            self.program['u_resolution'].value = (float(self.width), float(self.height))
            
            # Posición de la mano
            self.program['u_hand_pos'].value = self.hand_pos
            
            # Estado de detección
            self.program['u_hand_detected'].value = float(self.hand_detected)
            
            # Intensidad
            self.program['u_intensity'].value = float(self.intensity)
        
        # Renderizar quad
        if self.vao:
            self.vao.render()
        
        # Intercambiar buffers
        pygame.display.flip()
        
        # Limitar FPS
        self.clock.tick(60)
        
        return True
    
    def _toggle_fullscreen(self):
        """Alterna entre modo ventana y pantalla completa."""
        self.fullscreen = not self.fullscreen
        
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
            
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
    
    def get_fps(self) -> float:
        """
        Obtiene los FPS actuales.
        
        Returns:
            FPS actuales
        """
        if self.clock:
            return self.clock.get_fps()
        return 0.0
    
    def resize(self, width: int, height: int):
        """
        Redimensiona la ventana.
        
        Args:
            width: Nuevo ancho
            height: Nueva altura
        """
        self.width = width
        self.height = height
        
        if self.ctx:
            self.ctx.viewport = (0, 0, width, height)
        
        # Recrear ventana
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
            
        self.screen = pygame.display.set_mode((width, height), flags)
    
    def cleanup(self):
        """Libera recursos."""
        if self.vao:
            self.vao.release()
        if self.program:
            self.program.release()
        if self.ctx:
            self.ctx.release()
            
        pygame.quit()
        print("Renderer limpiado")
    
    def __del__(self):
        """Destructor para asegurar limpieza de recursos."""
        self.cleanup() 