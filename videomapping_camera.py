#!/usr/bin/env python3
"""
Videomapping interactivo para investigación posthumanista sobre ríos de Santiago.
Sistema que contrasta dos paradigmas fluviales:

MAPOCHO CANALIZADO: Río urbano constricto con respuesta dramática
MAIPO ABIERTO: Río natural libre con movimiento sutil

Implementa detección de movimiento con cámara web usando OpenCV.
Renderizado en tiempo real con Pygame a 1920x1080.
Interacción sin artefactos visuales mediante filtrado de puntos.

Controles:
- Movimiento en cámara: Manipular agua
- ESPACIO: Cambiar río
- C: Activar/desactivar cámara  
- F11: Pantalla completa
- ESC: Salir
"""

import pygame
import cv2
import math
import numpy as np
import threading
import time

class MovementDetector:
    """Detecta movimiento en tiempo real usando background subtraction de OpenCV."""
    
    def __init__(self):
        # Variables de estado de cámara
        self.cap = None
        self.camera_active = False
        self.movement_position = (960, 540)  # Posición central por defecto
        self.camera_thread = None
        self.running = False
        
        # Mapeo a resolución de pantalla
        self.screen_width = 1920
        self.screen_height = 1080
        
        # Background subtractor para detectar movimiento
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.movement_detected = False
        
    def start_camera(self):
        """Inicializa la cámara web y comienza el procesamiento en thread separado."""
        if self.camera_active:
            return
            
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("No se pudo abrir la cámara")
                return
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.camera_active = True
            self.running = True
            self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
            self.camera_thread.start()
            
            print("Cámara iniciada - Muévete para interactuar")
            
        except Exception as e:
            print(f"Error al iniciar cámara: {e}")
    
    def stop_camera(self):
        """Detiene la cámara y libera recursos."""
        self.running = False
        self.camera_active = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.movement_detected = False
        print("Cámara detenida")
    
    def _camera_loop(self):
        """Loop principal que procesa frames de la cámara y detecta movimiento."""
        while self.running and self.cap:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Flip horizontal para que sea como un espejo
                frame = cv2.flip(frame, 1)
                
                # Aplicar background subtraction para detectar cambios
                fg_mask = self.background_subtractor.apply(frame)
                
                # Encontrar contornos en la máscara de foreground
                contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Reset del estado de detección
                self.movement_detected = False
                
                if contours:
                    # Tomar el contorno de mayor área
                    largest_contour = max(contours, key=cv2.contourArea)
                    area = cv2.contourArea(largest_contour)
                    
                    # Filtrar movimientos pequeños (ruido)
                    if area > 500:
                        self.movement_detected = True
                        
                        # Calcular centroide del movimiento
                        M = cv2.moments(largest_contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            
                            # Mapear coordenadas de cámara a pantalla
                            screen_x = int((cx / 640) * self.screen_width)
                            screen_y = int((cy / 480) * self.screen_height)
                            
                            self.movement_position = (screen_x, screen_y)
                            
                            # Visualización para debug
                            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)
                            cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
                
                # Mostrar frame con overlays de debug
                cv2.imshow('Detección de Movimiento - VideomappingART', frame)
                cv2.waitKey(1)
                
            except Exception as e:
                print(f"Error en procesamiento de cámara: {e}")
                time.sleep(0.1)
    
    def get_movement(self):
        """Retorna la posición actual del movimiento detectado o lista vacía."""
        if self.camera_active and self.movement_detected:
            return [self.movement_position]
        return []
    
    def toggle_camera(self):
        """Alterna el estado de la cámara entre activada y desactivada."""
        if self.camera_active:
            self.stop_camera()
        else:
            self.start_camera()
    
    def cleanup(self):
        """Libera recursos y cierra ventanas de OpenCV."""
        self.stop_camera()
        cv2.destroyAllWindows()

class PygameRiosRenderer:
    """Renderiza los efectos visuales de los ríos usando Pygame."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.time = 0
        
        # Estado del sistema
        self.current_effect = "MAPOCHO"  # MAPOCHO o MAIPO
        
        # Tracking de posición de interacción
        self.mouse_x = width // 2
        self.mouse_y = height // 2
        self.mouse_active = False
        
        # Configuración del Mapocho se define dinámicamente en render
        
        # Configuración del Maipo: 5 brazos con grosores variados
        self.maipo_widths = [6, 18, 3, 25, 12]  # Contraste dramático de anchos
        self.maipo_colors = [
            (60, 140, 200),   # Azul medio
            (40, 160, 220),   # Azul brillante  
            (80, 120, 180),   # Azul oscuro
            (50, 180, 240),   # Azul claro
            (70, 130, 190)    # Azul estándar
        ]

    def update_movement(self, movement_positions):
        """Actualiza la posición de interacción desde detección de movimiento."""
        if movement_positions:
            # Usar la primera posición detectada
            self.mouse_x, self.mouse_y = movement_positions[0]
            self.mouse_active = True
        else:
            self.mouse_active = False

    def update_mouse(self, mouse_pos, mouse_pressed):
        """Fallback para usar mouse cuando no hay cámara activa."""
        self.mouse_x, self.mouse_y = mouse_pos
        self.mouse_active = mouse_pressed

    def draw_smooth_line(self, surface, color, points, width):
        """Dibuja líneas suaves con filtrado de puntos para evitar artefactos visuales."""
        if len(points) < 2:
            return
        
        # Filtrar puntos para evitar saltos que generan artefactos
        filtered_points = []
        for i, point in enumerate(points):
            if i == 0:
                filtered_points.append(point)
            else:
                # Solo añadir punto si la distancia es razonable
                prev_point = filtered_points[-1]
                distance = math.sqrt((point[0] - prev_point[0])**2 + (point[1] - prev_point[1])**2)
                if distance < 50:  # Threshold para saltos
                    filtered_points.append(point)
                else:
                    # Interpolar punto intermedio para suavidad
                    mid_x = (point[0] + prev_point[0]) / 2
                    mid_y = (point[1] + prev_point[1]) / 2
                    filtered_points.append((mid_x, mid_y))
                    filtered_points.append(point)
        
        if len(filtered_points) < 2:
            return
        
        # Línea principal sólida
        pygame.draw.lines(surface, color, False, filtered_points, max(1, width))
        
        # Glow sutil para líneas gruesas
        if width > 3:
            glow_color = (
                max(0, color[0] - 20),
                max(0, color[1] - 20),
                max(0, color[2] - 20)
            )
            pygame.draw.lines(surface, glow_color, False, filtered_points, max(1, width + 2))

    def render_mapocho_canalizado(self, surface):
        """Renderiza el Mapocho como canal urbano constricto con respuesta dramática."""
        
        # Estructura del canal de hormigón
        canal_y = self.height // 2
        canal_width = 180
        canal_top = canal_y - canal_width // 2
        canal_bottom = canal_y + canal_width // 2
        
        # Base de hormigón del canal
        canal_rect = pygame.Rect(0, canal_top, self.width, canal_width)
        pygame.draw.rect(surface, (40, 45, 55), canal_rect)
        
        # Muros laterales del canal
        borde_color = (80, 85, 95)
        pygame.draw.line(surface, borde_color, (0, canal_top), (self.width, canal_top), 12)
        pygame.draw.line(surface, borde_color, (0, canal_bottom), (self.width, canal_bottom), 12)
        
        # Sombras internas para dar profundidad
        sombra_color = (25, 30, 40)
        pygame.draw.line(surface, sombra_color, (0, canal_top + 12), (self.width, canal_top + 12), 4)
        pygame.draw.line(surface, sombra_color, (0, canal_bottom - 12), (self.width, canal_bottom - 12), 4)
        
        # Agua constreñida dentro del canal
        # 8 líneas de agua horizontales distribuidas en el canal
        num_lines = 8
        for i in range(num_lines):
            # Distribución vertical dentro del canal
            line_y_offset = (i / (num_lines - 1)) * (canal_width * 0.6) - (canal_width * 0.3)
            base_y = canal_y + line_y_offset
            
            line_points = []
            
            for x in range(0, self.width, 4):  # Puntos cada 4px para suavidad
                # Ondulación base con componente aleatoria
                wave_base = math.sin(self.time * 1.0 + x * 0.006 + i * 0.5) * 3
                random_flutter = math.sin(self.time * 3.2 + x * 0.015 + i * 1.2) * 1.5
                
                # Interacción dramática con movimiento detectado
                hand_influence = 0
                if self.mouse_active:
                    dist_to_hand = abs(self.mouse_y - base_y)
                    horizontal_dist = abs(self.mouse_x - x)
                    
                    # Zona de influencia ampliada para efecto dramático
                    if dist_to_hand < 120 and horizontal_dist < 250:
                        influence_strength = 1.0 - (dist_to_hand / 120.0)
                        horizontal_factor = 1.0 - (horizontal_dist / 250.0)
                        
                        # Ondulación de amplitud máxima (80px)
                        hand_influence = math.sin(self.time * 6 + x * 0.012) * 80 * influence_strength * horizontal_factor
                
                # Calcular posición final limitada al canal
                y_final = base_y + wave_base + random_flutter + hand_influence
                y_final = max(canal_top + 20, min(canal_bottom - 20, y_final))
                
                line_points.append((x, y_final))
            
            # Renderizar línea de agua
            if len(line_points) > 1:
                intensity = 0.7 + 0.3 * math.sin(self.time * 1.2 + i * 0.4)
                if self.mouse_active and abs(self.mouse_y - base_y) < 120:
                    intensity = 1.0
                
                # Colores azules fríos característicos del agua urbana
                r_core = int(60 + intensity * 80)
                g_core = int(130 + intensity * 90)
                b_core = int(200 + intensity * 55)
                
                color_core = (r_core, g_core, b_core)
                
                # Dibujar línea con filtrado suave
                self.draw_smooth_line(surface, color_core, line_points, 4)

    def render_maipo_abierto(self, surface):
        """Renderiza el Maipo como río natural libre con movimiento sutil."""
        
        # Sistema de múltiples brazos fluviales
        # 5 brazos principales con grosores contrastantes
        num_brazos = 5
        for i in range(num_brazos):
            brazo_path = []
            
            # Trayectoria base de cada brazo
            y_brazo_base = self.height * (0.3 + i * 0.1)  # Distribución vertical
            
            for x in range(0, self.width, 3):  # Puntos cada 3px para máxima suavidad
                # Meandros naturales de diferentes escalas
                meander_principal = math.sin(x * 0.004 + i * 1.5) * 80
                meander_secundario = math.sin(x * 0.012 + self.time * 0.8 + i) * 30
                turbulencia = math.sin(x * 0.03 + self.time * 2) * 10
                
                # Sistema multicapa de aleatoriedad orgánica
                random_organic1 = math.sin(self.time * 2.5 + x * 0.008 + i * 0.7) * 15
                random_organic2 = math.cos(self.time * 1.8 + x * 0.005 + i * 1.2) * 8
                random_organic3 = math.sin(self.time * 3.2 + x * 0.015 + i * 0.4) * 5
                
                # Variación lenta temporal para cada brazo
                long_term_variation = math.sin(self.time * 0.3 + i * 2.0) * 20
                
                # Combinación total de movimiento aleatorio
                total_randomness = random_organic1 + random_organic2 + random_organic3 + long_term_variation
                
                # Interacción sutil con movimiento detectado
                hand_influence_x = 0
                hand_influence_y = 0
                
                if self.mouse_active:
                    base_y_current = y_brazo_base + meander_principal + meander_secundario
                    dist_to_hand = math.sqrt((self.mouse_x - x)**2 + (self.mouse_y - base_y_current)**2)
                    
                    # Zona de influencia amplia para río abierto
                    if dist_to_hand < 400:
                        influence_strength = 1.0 - (dist_to_hand / 400.0)
                        
                        # Elevación vertical siguiendo la altura de la interacción
                        vertical_diff = self.mouse_y - base_y_current
                        
                        # Factor de elevación aumentado para respuesta clara
                        elevation_factor = vertical_diff * influence_strength * 1.2
                        
                        # Ondulación sutil para mantener fluidez
                        subtle_wave = math.sin(self.time * 3 + x * 0.01) * 8 * influence_strength
                        
                        # Solo movimiento vertical (sin horizontal)
                        hand_influence_x = 0
                        hand_influence_y = elevation_factor + subtle_wave
                
                # Calcular posición final del brazo
                x_final = x + hand_influence_x
                y_final = y_brazo_base + meander_principal + meander_secundario + turbulencia + total_randomness + hand_influence_y
                
                # Clamp dentro de los límites de pantalla
                x_final = max(0, min(self.width, x_final))
                y_final = max(50, min(self.height - 50, y_final))
                
                brazo_path.append((x_final, y_final))
            
            # Renderizar brazo del río
            if len(brazo_path) > 1:
                # Intensidad base variable por brazo
                base_intensity = 0.6 + 0.4 * math.sin(self.time * 1.5 + i * 0.8)
                
                # Aumentar intensidad con interacción
                intensity = base_intensity
                if self.mouse_active:
                    min_dist = min(math.sqrt((self.mouse_x - x)**2 + (self.mouse_y - y)**2) 
                                 for x, y in brazo_path)
                    if min_dist < 400:
                        intensity = 1.0
                
                # Paleta natural verde-azulada
                r_core = int(40 + intensity * 60)
                g_core = int(100 + intensity * 120)
                b_core = int(160 + intensity * 95)
                
                color_core = (r_core, g_core, b_core)
                
                # Aplicar grosor específico del brazo
                width = self.maipo_widths[i % len(self.maipo_widths)]
                
                # Dibujar con filtrado suave
                self.draw_smooth_line(surface, color_core, brazo_path, width)

    def render(self, surface):
        """Renderiza el frame actual del sistema."""
        # Limpiar pantalla
        surface.fill((0, 0, 0))
        
        # Incrementar tiempo de animación
        self.time += 0.016  # 60 FPS
        
        # Renderizar el efecto seleccionado
        if self.current_effect == "MAPOCHO":
            self.render_mapocho_canalizado(surface)
        else:  # MAIPO
            self.render_maipo_abierto(surface)
    
    def switch_effect(self):
        """Alterna entre los dos paradigmas fluviales."""
        if self.current_effect == "MAPOCHO":
            self.current_effect = "MAIPO"
            print("Cambiado a efecto: RÍO MAIPO (Abierto y Natural)")
        else:
            self.current_effect = "MAPOCHO"
            print("Cambiado a efecto: RÍO MAPOCHO (Canalizado y Urbano)")

class VideomappingApp:
    """Aplicación principal del sistema de videomapping interactivo."""
    
    def __init__(self):
        pygame.init()
        
        # Configuración de pantalla Full HD
        self.width, self.height = 1920, 1080
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Videomapping Ríos Interactivos - Detección de Movimiento")
        
        # Inicialización de componentes
        self.renderer = PygameRiosRenderer(self.width, self.height)
        self.movement_detector = MovementDetector()
        
        # Variables de control
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Activar cámara al inicio
        self.movement_detector.start_camera()
        
        print("VIDEOMAPPING RÍOS INTERACTIVOS")
        print("   Detección de movimiento con cámara web")
        print("   Renderizado sin artefactos visuales")
        print("   Sistema de aleatoriedad orgánica multicapa")
        print("   - Movimiento: Manipular agua interactivamente")
        print("   - ESPACIO: Cambiar río")
        print("   - C: Activar/desactivar cámara")
        print("   - F11: Pantalla completa")
        print("   - ESC: Salir")
        print(f"   - Efecto actual: RÍO {self.renderer.current_effect}")

    def handle_events(self):
        """Procesa eventos de teclado y sistema."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.renderer.switch_effect()
                elif event.key == pygame.K_c:
                    self.movement_detector.toggle_camera()
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    print("Alternando pantalla completa")

    def update(self):
        """Actualiza el estado del sistema por frame."""
        # Obtener posiciones desde detector de movimiento
        movements = self.movement_detector.get_movement()
        
        if movements:
            # Usar posición detectada por cámara
            self.renderer.update_movement(movements)
        else:
            # Fallback a mouse como entrada alternativa
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
            self.renderer.update_mouse(mouse_pos, mouse_pressed)

    def run(self):
        """Loop principal de la aplicación."""
        print("Iniciando videomapping con detección de movimiento...")
        print("   Ventana: 1920x1080 (Full HD)")
        print("   Muévete frente a la cámara para interactuar")
        print("   Si no ves nada, presiona ALT+TAB para buscar la ventana")
        
        try:
            while self.running:
                self.handle_events()
                self.update()
                
                # Renderizar frame actual
                self.renderer.render(self.screen)
                
                # Actualizar display
                pygame.display.flip()
                self.clock.tick(60)  # Mantener 60 FPS
                
        except KeyboardInterrupt:
            print("\nVideomapping interrumpido por el usuario")
        finally:
            self.cleanup()

    def cleanup(self):
        """Limpia recursos al cerrar la aplicación."""
        print("Cerrando videomapping...")
        self.movement_detector.cleanup()
        pygame.quit()
        print("Videomapping cerrado")

def main():
    """Función principal del programa."""
    try:
        app = VideomappingApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()