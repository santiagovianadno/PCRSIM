"""
Visualizador de Basteria PLY con Control Dual de Manos (Modo Prueba)
- Mano derecha: Control de cámara (rotación y zoom)
- Mano izquierda: Efectos visuales (color y opacidad)
"""

import pygame
from pygame .locals import *
from OpenGL .GL import *
from OpenGL .GLU import *
import numpy as np
import time
from ply_cell_renderer import PLYCellModel

class BasteriaViewer :
    def __init__ (self ,ply_file ='models/basteria2.ply'):
        print (' Inicializando Visualizador Basteria...')


        pygame .init ()


        self .screen_width =1200
        self .screen_height =800
        self .screen =pygame .display .set_mode ((self .screen_width ,self .screen_height ),DOUBLEBUF |OPENGL )
        pygame .display .set_caption (' Visualizador Basteria - Control Dual de Manos')


        self .setup_opengl ()


        print (f' Cargando modelo: {ply_file}')
        self .model =PLYCellModel (ply_file )


        self .camera_distance =15.0
        self .camera_rotation_x =0.0
        self .camera_rotation_y =0.0


        self .model_color =[1.0 ,1.0 ,1.0 ]
        self .model_opacity =1.0
        self .is_red_mode =False


        self .simulate_hands =True
        self .time_offset =0


        self .mouse_pressed =False
        self .last_mouse_pos =None

        print (' Inicialización completa')

    def setup_opengl (self ):
        """Configura OpenGL"""
        glEnable (GL_DEPTH_TEST )
        glDepthFunc (GL_LESS )


        glMatrixMode (GL_PROJECTION )
        gluPerspective (45 ,(self .screen_width /self .screen_height ),0.1 ,100.0 )
        glMatrixMode (GL_MODELVIEW )


        glClearColor (0.05 ,0.05 ,0.1 ,1.0 )

    def simulate_hand_controls (self ):
        """Simula controles de mano para demostrar funcionalidad"""
        current_time =time .time ()+self .time_offset



        self .camera_rotation_y +=0.5


        zoom_factor =np .sin (current_time *0.5 )*0.3
        self .camera_distance =15.0 +zoom_factor *10.0



        color_cycle =np .sin (current_time *0.8 )
        if color_cycle >0.5 :
            self .is_red_mode =True
            self .model_color =[1.0 ,0.0 ,0.0 ]
        else :
            self .is_red_mode =False
            self .model_color =[1.0 ,1.0 ,1.0 ]


        opacity_cycle =(np .sin (current_time *1.2 )+1.0 )/2.0
        self .model_opacity =0.3 +opacity_cycle *0.7

    def handle_mouse_input (self ):
        """Maneja entrada del mouse como control alternativo"""
        mouse_pos =pygame .mouse .get_pos ()
        mouse_buttons =pygame .mouse .get_pressed ()

        if mouse_buttons [0 ]:
            if self .last_mouse_pos is not None :
                dx =mouse_pos [0 ]-self .last_mouse_pos [0 ]
                dy =mouse_pos [1 ]-self .last_mouse_pos [1 ]

                self .camera_rotation_y +=dx *0.5
                self .camera_rotation_x +=dy *0.5

        self .last_mouse_pos =mouse_pos if mouse_buttons [0 ]else None


        keys =pygame .key .get_pressed ()
        if keys [K_PLUS ]or keys [K_EQUALS ]:
            self .camera_distance =max (2.0 ,self .camera_distance -0.5 )
        if keys [K_MINUS ]:
            self .camera_distance =min (50.0 ,self .camera_distance +0.5 )

    def render_model (self ):
        """Renderiza el modelo PLY con color y opacidad dinámicos"""
        if len (self .model .vertices )>0 :

            glEnable (GL_BLEND )
            glBlendFunc (GL_SRC_ALPHA ,GL_ONE_MINUS_SRC_ALPHA )


            glColor4f (self .model_color [0 ],self .model_color [1 ],self .model_color [2 ],self .model_opacity )

            glEnableClientState (GL_VERTEX_ARRAY )

            glVertexPointer (3 ,GL_FLOAT ,0 ,self .model .vertices )

            glPointSize (2.0 )
            glDrawArrays (GL_POINTS ,0 ,len (self .model .vertices ))

            glDisableClientState (GL_VERTEX_ARRAY )

            glDisable (GL_BLEND )

    def render_ui (self ):
        """Renderiza información en pantalla"""

        pass

    def run (self ):
        """Bucle principal"""
        try :
            clock =pygame .time .Clock ()
            running =True

            print (" Visualizador Basteria con Control Dual de Manos iniciado (MODO PRUEBA)")
            print (" Controles:")
            print ("\n SIMULACIÓN AUTOMÁTICA:")
            print ("   - Rotación automática del modelo")
            print ("   - Zoom oscilante")
            print ("   - Cambio de color automático (blanco ↔ rojo)")
            print ("   - Opacidad variable")
            print ("\n⌨️  Controles manuales:")
            print ("   ️  Mouse: Arrastrar para rotar")
            print ("    +/-: Zoom in/out")
            print ("    R: Reset cámara")
            print ("   ⏸️  ESPACIO: Pausar/reanudar simulación")
            print ("    ESC: Salir")
            print (f"\n Mostrando {len(self.model.vertices):,} vértices de tu models/basteria2.ply")
            print (" Observa los cambios automáticos de color y opacidad")

            while running :
                for event in pygame .event .get ():
                    if event .type ==pygame .QUIT :
                        running =False
                    elif event .type ==pygame .KEYDOWN :
                        if event .key ==pygame .K_ESCAPE :
                            running =False
                        elif event .key ==pygame .K_r :

                            self .camera_distance =15.0
                            self .camera_rotation_x =0.0
                            self .camera_rotation_y =0.0
                            print (" Cámara reiniciada")
                        elif event .key ==pygame .K_SPACE :

                            self .simulate_hands =not self .simulate_hands
                            if not self .simulate_hands :
                                self .time_offset =time .time ()-self .time_offset
                            print (f"⏸️  Simulación: {'PAUSADA' if not self.simulate_hands else 'REANUDADA'}")
                    elif event .type ==pygame .MOUSEWHEEL :

                        self .camera_distance =max (2.0 ,min (50.0 ,self .camera_distance -event .y ))


                if self .simulate_hands :
                    self .simulate_hand_controls ()

                self .handle_mouse_input ()


                glClear (GL_COLOR_BUFFER_BIT |GL_DEPTH_BUFFER_BIT )


                glLoadIdentity ()
                glTranslatef (0 ,0 ,-self .camera_distance )
                glRotatef (self .camera_rotation_x ,1 ,0 ,0 )
                glRotatef (self .camera_rotation_y ,0 ,1 ,0 )


                self .render_model ()
                self .render_ui ()


                pygame .display .flip ()
                clock .tick (60 )

        except Exception as e :
            print (f" Error durante la ejecución: {e}")
        finally :
            pygame .quit ()
            print (" ¡Hasta luego!")

def main ():
    """Función principal"""
    try :
        viewer =BasteriaViewer ('models/basteria2.ply')
        viewer .run ()
    except Exception as e :
        print (f" Error al inicializar: {e}")
        print (" Asegúrate de que models/basteria2.ply existe en el directorio")

if __name__ =="__main__":
    main ()
