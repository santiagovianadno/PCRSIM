import pygame
import math
import random
import time

class PygameRiosRenderer:
    """Renderer de efectos de río realistas - Uno canalizado, otro abierto."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.time = 0
        
        # Mouse/Hand tracking
        self.mouse_x = width // 2
        self.mouse_y = height // 2
        self.mouse_active = False
        self.prev_mouse_x = width // 2
        self.prev_mouse_y = height // 2
        
        # Efectos
        self.current_effect = "MAPOCHO"  # MAPOCHO o MAIPO

    def update_mouse(self, mouse_pos, mouse_active):
        """Actualizar posición del mouse/mano."""
        self.prev_mouse_x = self.mouse_x
        self.prev_mouse_y = self.mouse_y
        self.mouse_x, self.mouse_y = mouse_pos
        self.mouse_active = mouse_active

    def draw_smooth_line(self, surface, color, points, width):
        """Dibujar línea suave con anti-aliasing mejorado SIN líneas negras."""
        if len(points) < 2:
            return
        
        # Filtrar puntos para evitar saltos bruscos que causan líneas negras
        filtered_points = []
        for i, point in enumerate(points):
            if i == 0:
                filtered_points.append(point)
            else:
                # Solo añadir punto si no está muy lejos del anterior
                prev_point = filtered_points[-1]
                distance = math.sqrt((point[0] - prev_point[0])**2 + (point[1] - prev_point[1])**2)
                if distance < 50:  # Límite para evitar saltos
                    filtered_points.append(point)
                else:
                    # Interpolar para suavizar saltos
                    mid_x = (point[0] + prev_point[0]) / 2
                    mid_y = (point[1] + prev_point[1]) / 2
                    filtered_points.append((mid_x, mid_y))
                    filtered_points.append(point)
        
        if len(filtered_points) < 2:
            return
        
        # Dibujar línea principal con color sólido (sin transparencias que causan líneas negras)
        pygame.draw.lines(surface, color, False, filtered_points, max(1, width))
        
        # Efecto glow suave opcional (solo si el grosor es mayor a 3)
        if width > 3:
            glow_color = (
                max(0, color[0] - 20),
                max(0, color[1] - 20),
                max(0, color[2] - 20)
            )
            pygame.draw.lines(surface, glow_color, False, filtered_points, max(1, width + 2))

    def render_mapocho_canalizado(self, surface):
        """MAPOCHO CANALIZADO: Canal estrecho y constreñido como río urbano."""
        
        # === ESTRUCTURA DE CANAL CANALIZADO ===
        canal_y = self.height // 2
        canal_width = 180  # Ancho del canal canalizado
        canal_top = canal_y - canal_width // 2
        canal_bottom = canal_y + canal_width // 2
        
        # Fondo del canal (hormigón)
        canal_rect = pygame.Rect(0, canal_top, self.width, canal_width)
        pygame.draw.rect(surface, (40, 45, 55), canal_rect)
        
        # Bordes del canal (muros de hormigón más definidos)
        borde_color = (80, 85, 95)
        pygame.draw.line(surface, borde_color, (0, canal_top), (self.width, canal_top), 12)
        pygame.draw.line(surface, borde_color, (0, canal_bottom), (self.width, canal_bottom), 12)
        
        # Sombras interiores para profundidad
        sombra_color = (25, 30, 40)
        pygame.draw.line(surface, sombra_color, (0, canal_top + 12), (self.width, canal_top + 12), 4)
        pygame.draw.line(surface, sombra_color, (0, canal_bottom - 12), (self.width, canal_bottom - 12), 4)
        
        # === AGUA CONSTREÑIDA (solo dentro del canal) ===
        # 8 líneas horizontales DENTRO del canal (2 más que antes)
        num_lines = 8
        for i in range(num_lines):
            # Posición Y dentro del canal (más espaciadas)
            line_y_offset = (i / (num_lines - 1)) * (canal_width * 0.6) - (canal_width * 0.3)
            base_y = canal_y + line_y_offset
            
            line_points = []
            
            for x in range(0, self.width, 4):  # Más puntos para mayor suavidad
                # Ondulación base con ALEATORIEDAD
                wave_base = math.sin(self.time * 1.0 + x * 0.006 + i * 0.5) * 3
                random_flutter = math.sin(self.time * 3.2 + x * 0.015 + i * 1.2) * 1.5  # Aleatoriedad
                
                # INTERACCIÓN CON MANOS - Ondulación EXAGERADAMENTE PODEROSA
                hand_influence = 0
                if self.mouse_active:
                    dist_to_hand = abs(self.mouse_y - base_y)
                    horizontal_dist = abs(self.mouse_x - x)
                    
                    # Zona de influencia MUCHO mayor para ondulación exagerada
                    if dist_to_hand < 120 and horizontal_dist < 250:
                        influence_strength = 1.0 - (dist_to_hand / 120.0)
                        horizontal_factor = 1.0 - (horizontal_dist / 250.0)
                        
                        # Ondulación EXAGERADAMENTE PODEROSA (amplitud máxima)
                        hand_influence = math.sin(self.time * 6 + x * 0.012) * 80 * influence_strength * horizontal_factor
                
                # Posición final LIMITADA al canal
                y_final = base_y + wave_base + random_flutter + hand_influence
                y_final = max(canal_top + 20, min(canal_bottom - 20, y_final))
                
                line_points.append((x, y_final))
            
            # Dibujar línea suave (SIN efecto blanco)
            if len(line_points) > 1:
                intensity = 0.7 + 0.3 * math.sin(self.time * 1.2 + i * 0.4)
                if self.mouse_active and abs(self.mouse_y - base_y) < 120:
                    intensity = 1.0
                
                # Colores azules fríos (agua canalizada/urbana)
                r_core = int(60 + intensity * 80)
                g_core = int(130 + intensity * 90)
                b_core = int(200 + intensity * 55)
                
                color_core = (r_core, g_core, b_core)
                
                # Usar función de dibujo suave (sin efectos adicionales)
                self.draw_smooth_line(surface, color_core, line_points, 4)
                
                # SIN brillo extra blanco (eliminado)

    def render_maipo_abierto(self, surface):
        """MAIPO ABIERTO: Río natural amplio con múltiples brazos."""
        
        # === SIN FONDO GRIS-VERDE ===
        # Solo fondo negro, sin lecho visible
        
        # === MÚLTIPLES BRAZOS DE AGUA ===
        # 5 brazos principales del río con GROSORES MUY VARIADOS
        num_brazos = 5
        for i in range(num_brazos):
            brazo_path = []
            
            # Cada brazo tiene su propia trayectoria natural
            y_brazo_base = self.height * (0.3 + i * 0.1)  # Distribuidos naturalmente
            
            for x in range(0, self.width, 3):  # Máxima suavidad
                # Meandros naturales amplios con ALEATORIEDAD MEJORADA
                meander_principal = math.sin(x * 0.004 + i * 1.5) * 80
                meander_secundario = math.sin(x * 0.012 + self.time * 0.8 + i) * 30
                turbulencia = math.sin(x * 0.03 + self.time * 2) * 10
                
                # MÚLTIPLES CAPAS DE ALEATORIEDAD para naturalidad orgánica
                random_organic1 = math.sin(self.time * 2.5 + x * 0.008 + i * 0.7) * 15
                random_organic2 = math.cos(self.time * 1.8 + x * 0.005 + i * 1.2) * 8
                random_organic3 = math.sin(self.time * 3.2 + x * 0.015 + i * 0.4) * 5
                
                # Variación lenta de largo plazo para cada brazo
                long_term_variation = math.sin(self.time * 0.3 + i * 2.0) * 20
                
                # Combinación de todas las aleatoriedades
                total_randomness = random_organic1 + random_organic2 + random_organic3 + long_term_variation
                
                # INTERACCIÓN CON MANOS - Movimiento MÁS FUERTE hacia arriba/abajo
                hand_influence_x = 0
                hand_influence_y = 0
                
                if self.mouse_active:
                    base_y_current = y_brazo_base + meander_principal + meander_secundario
                    dist_to_hand = math.sqrt((self.mouse_x - x)**2 + (self.mouse_y - base_y_current)**2)
                    
                    # Zona de influencia EXAGERADAMENTE AMPLIA (río abierto)
                    if dist_to_hand < 400:
                        influence_strength = 1.0 - (dist_to_hand / 400.0)
                        
                        # MOVIMIENTO FUERTE hacia arriba/abajo con las manos
                        vertical_diff = self.mouse_y - base_y_current
                        
                        # Movimiento MÁS FUERTE hacia la altura de la mano
                        elevation_factor = vertical_diff * influence_strength * 1.2  # Factor muy aumentado
                        
                        # Pequeña ondulación natural para que no sea estático
                        subtle_wave = math.sin(self.time * 3 + x * 0.01) * 8 * influence_strength
                        
                        # Aplicar solo movimiento vertical fuerte
                        hand_influence_x = 0  # Sin movimiento horizontal
                        hand_influence_y = elevation_factor + subtle_wave
                
                # Posición final del brazo
                x_final = x + hand_influence_x
                y_final = y_brazo_base + meander_principal + meander_secundario + turbulencia + total_randomness + hand_influence_y
                
                # Mantener dentro de la pantalla
                x_final = max(0, min(self.width, x_final))
                y_final = max(50, min(self.height - 50, y_final))
                
                brazo_path.append((x_final, y_final))
            
            # Dibujar brazo del río (SIN partículas cyan ni líneas negras)
            if len(brazo_path) > 1:
                # Intensidad variable por brazo
                base_intensity = 0.6 + 0.4 * math.sin(self.time * 1.5 + i * 0.8)
                
                # Incrementar intensidad si hay interacción
                intensity = base_intensity
                if self.mouse_active:
                    min_dist = min(math.sqrt((self.mouse_x - x)**2 + (self.mouse_y - y)**2) 
                                 for x, y in brazo_path)
                    if min_dist < 400:
                        intensity = 1.0
                
                # Colores verdes-azules naturales
                r_core = int(40 + intensity * 60)
                g_core = int(100 + intensity * 120)
                b_core = int(160 + intensity * 95)
                
                color_core = (r_core, g_core, b_core)
                
                # GROSORES MUY EXAGERADOS (más variación)
                widths = [6, 18, 3, 25, 12]  # Mucha más variación
                width = widths[i % len(widths)]
                
                # Dibujar con máxima suavidad (SIN efectos adicionales)
                self.draw_smooth_line(surface, color_core, brazo_path, width)
                
                # SIN partículas cyan ni efectos adicionales (eliminados)

    def render(self, surface):
        """Renderizar efecto actual."""
        # Fondo negro
        surface.fill((0, 0, 0))
        
        # Actualizar tiempo
        self.time += 0.016  # ~60 FPS
        
        # Renderizar efecto actual
        if self.current_effect == "MAPOCHO":
            self.render_mapocho_canalizado(surface)
        else:  # MAIPO
            self.render_maipo_abierto(surface)
    
    def switch_effect(self):
        """Cambiar entre efectos."""
        if self.current_effect == "MAPOCHO":
            self.current_effect = "MAIPO"
            print("🌊 Cambiado a efecto: RÍO MAIPO (Abierto y Natural)")
        else:
            self.current_effect = "MAPOCHO"
            print("🌊 Cambiado a efecto: RÍO MAPOCHO (Canalizado y Urbano)")

class PygameVideomappingApp:
    """Aplicación principal de videomapping."""
    
    def __init__(self):
        pygame.init()
        
        # Configurar ventana FULL HD
        self.width, self.height = 1920, 1080  # Full HD
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("🌊 RÍOS REALISTAS - Canalizado vs Abierto")
        
        # Renderer
        self.renderer = PygameRiosRenderer(self.width, self.height)
        
        # Control
        self.clock = pygame.time.Clock()
        self.running = True
        
        print("🌊 VIDEOMAPPING RÍOS REALISTAS")
        print("   ✅ Sin pixelado - Calidad mejorada")
        print("   - Mouse/Mano: Manipular agua")
        print("   - ESPACIO: Cambiar río (Mapocho ↔ Maipo)")
        print("   - F11: Pantalla completa")
        print("   - ESC: Salir")
        print(f"   - Efecto actual: RÍO {self.renderer.current_effect}")

    def handle_events(self):
        """Manejar eventos."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.renderer.switch_effect()
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    print("🖥️ Alternando pantalla completa")

    def update(self):
        """Actualizar estado."""
        # Actualizar posición del mouse/mano
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Botón izquierdo o presencia de mano
        
        self.renderer.update_mouse(mouse_pos, mouse_pressed)

    def run(self):
        """Bucle principal."""
        print("🚀 Iniciando ríos realistas...")
        print("   📺 Ventana: 1920x1080 (Full HD)")
        print("   🎮 Si no ves nada, presiona ALT+TAB para buscar la ventana")
        
        while self.running:
            self.handle_events()
            self.update()
            
            # Renderizar
            self.renderer.render(self.screen)
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        print("👋 ¡Videomapping cerrado!")
        pygame.quit()

def main():
    """Función principal."""
    try:
        app = PygameVideomappingApp()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Videomapping interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 