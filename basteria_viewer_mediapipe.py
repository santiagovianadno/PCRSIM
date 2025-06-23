"""
Visualizador de Basteria PLY con Control Dual de Manos (MediaPipe)
- Mano derecha: Control de cámara (rotación y zoom con pinch)
- Mano izquierda: Efectos visuales (color con pinch + opacidad con movimiento)
"""

import pygame
from pygame .locals import *
from OpenGL .GL import *
from OpenGL .GLU import *
import numpy as np
import cv2
import mediapipe as mp
import math
import time
from plyfile import PlyData


mp_hands =mp .solutions .hands
mp_drawing =mp .solutions .drawing_utils
mp_drawing_styles =mp .solutions .drawing_styles

class SimplePLYLoader :
    """Cargador simple y robusto para archivos PLY"""

    def __init__ (self ,filename ):
        self .vertices =[]
        self .colors =[]
        self .vertex_count =0
        self .load_ply (filename )

    def load_ply (self ,filename ):
        """Carga archivo PLY con manejo robusto de errores"""
        try :
            print (f" Cargando {filename}...")
            plydata =PlyData .read (filename )

            if 'vertex'in plydata :
                vertex_data =plydata ['vertex']
                print (f" Vértices encontrados: {len(vertex_data)}")


                if hasattr (vertex_data ,'dtype')and vertex_data .dtype .names :
                    prop_names =vertex_data .dtype .names
                    print (f" Propiedades disponibles: {prop_names}")

                    if 'x'in prop_names and 'y'in prop_names and 'z'in prop_names :

                        vertices_raw =np .column_stack ([
                        vertex_data ['x'],
                        vertex_data ['y'],
                        vertex_data ['z']
                        ])


                        total_vertices =len (vertices_raw )
                        max_vertices =50000

                        if total_vertices >max_vertices :
                            step =total_vertices //max_vertices
                            self .vertices =vertices_raw [::step ]
                            print (f" Submuestreo aplicado: {len(self.vertices)} de {total_vertices} vértices")
                        else :
                            self .vertices =vertices_raw
                            print (f" Usando todos los vértices: {len(self.vertices)}")


                        if len (self .vertices )>0 :
                            center =np .mean (self .vertices ,axis =0 )
                            self .vertices -=center


                            max_coord =np .max (np .abs (self .vertices ))
                            if max_coord >0 :
                                scale_factor =8.0 /max_coord
                                self .vertices *=scale_factor

                            self .vertex_count =len (self .vertices )


                            self .colors =np .full ((self .vertex_count ,3 ),[1.0 ,1.0 ,1.0 ],dtype =np .float32 )

                            print (f" Modelo procesado: {self.vertex_count} vértices")
                            return

                print (" No se encontraron coordenadas x,y,z válidas")
            else :
                print (" No se encontró sección 'vertex' en el PLY")

        except Exception as e :
            print (f" Error cargando PLY: {e}")


        print (" Creando geometría de respaldo...")
        self .create_fallback_geometry ()

    def create_fallback_geometry (self ):
        """Crea una esfera simple como respaldo"""
        vertices =[]
        for i in range (20 ):
            for j in range (20 ):
                theta =(i /19.0 )*math .pi
                phi =(j /19.0 )*2 *math .pi

                x =math .sin (theta )*math .cos (phi )*3.0
                y =math .sin (theta )*math .sin (phi )*3.0
                z =math .cos (theta )*3.0

                vertices .append ([x ,y ,z ])

        self .vertices =np .array (vertices ,dtype =np .float32 )
        self .vertex_count =len (self .vertices )
        self .colors =np .full ((self .vertex_count ,3 ),[1.0 ,1.0 ,1.0 ],dtype =np .float32 )
        print (f" Geometría de respaldo creada: {self.vertex_count} vértices")

class BasteriaViewerMediaPipe :
    """Visualizador con controles duales de mano usando MediaPipe"""

    def __init__ (self ,ply_file ='models/basteria2.ply'):
        print (' Inicializando Visualizador Basteria con MediaPipe...')


        pygame .init ()


        self .screen_width =1200
        self .screen_height =800
        self .screen =pygame .display .set_mode ((self .screen_width ,self .screen_height ),DOUBLEBUF |OPENGL )
        pygame .display .set_caption (' Visualizador Basteria - Control Dual MediaPipe')


        self .setup_opengl ()


        print (f' Cargando modelo: {ply_file}')
        self .model =SimplePLYLoader (ply_file )


        self .camera_distance =15.0
        self .camera_rotation_x =0.0
        self .camera_rotation_y =0.0


        self .model_color =[1.0 ,1.0 ,1.0 ]
        self .model_opacity =1.0
        self .is_red_mode =False


        print (' Inicializando MediaPipe...')
        self .hands =mp_hands .Hands (
        model_complexity =1 ,
        min_detection_confidence =0.7 ,
        min_tracking_confidence =0.7 ,
        max_num_hands =2
        )


        print (' Inicializando cámara...')
        self .cap =cv2 .VideoCapture (0 )
        self .cap .set (cv2 .CAP_PROP_FRAME_WIDTH ,640 )
        self .cap .set (cv2 .CAP_PROP_FRAME_HEIGHT ,480 )


        self .show_camera =True
        self .hand_control_enabled =True
        self .last_right_hand_pos =None
        self .last_left_hand_pos =None


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

    def calculate_pinch_distance (self ,hand_landmarks ):
        """Calcula la distancia entre pulgar e índice para gesto de pinch"""
        thumb_tip =hand_landmarks .landmark [4 ]
        index_tip =hand_landmarks .landmark [8 ]


        distance =math .sqrt (
        (thumb_tip .x -index_tip .x )**2 +
        (thumb_tip .y -index_tip .y )**2
        )
        return distance

    def process_hand_tracking (self ):
        """Procesa el tracking de manos para controlar la cámara y efectos visuales"""
        if not self .hand_control_enabled :
            return

        ret ,frame =self .cap .read ()
        if not ret :
            return

        frame =cv2 .flip (frame ,1 )
        rgb_frame =cv2 .cvtColor (frame ,cv2 .COLOR_BGR2RGB )
        results =self .hands .process (rgb_frame )

        if results .multi_hand_landmarks and results .multi_handedness :
            for hand_landmarks ,handedness in zip (results .multi_hand_landmarks ,results .multi_handedness ):

                hand_label =handedness .classification [0 ].label
                is_right_hand =hand_label =="Right"


                palm =hand_landmarks .landmark [9 ]
                hand_x =palm .x
                hand_y =palm .y

                if is_right_hand :

                    self .process_right_hand (hand_landmarks ,hand_x ,hand_y ,frame )
                else :

                    self .process_left_hand (hand_landmarks ,hand_x ,hand_y ,frame )


                if self .show_camera :

                    color =(255 ,0 ,0 )if is_right_hand else (0 ,255 ,0 )
                    connections_color =mp_drawing_styles .DrawingSpec (color =color ,thickness =2 )
                    landmarks_color =mp_drawing_styles .DrawingSpec (color =color ,thickness =2 ,circle_radius =2 )

                    mp_drawing .draw_landmarks (
                    frame ,hand_landmarks ,mp_hands .HAND_CONNECTIONS ,
                    landmarks_color ,connections_color
                    )
        else :
            self .last_right_hand_pos =None
            self .last_left_hand_pos =None


        if self .show_camera :
            h ,w ,_ =frame .shape


            cv2 .putText (frame ,f"Zoom: {self.camera_distance:.1f}",(10 ,30 ),
            cv2 .FONT_HERSHEY_SIMPLEX ,0.6 ,(255 ,255 ,255 ),2 )
            cv2 .putText (frame ,f"Color: {'ROJO' if self.is_red_mode else 'BLANCO'}",(10 ,60 ),
            cv2 .FONT_HERSHEY_SIMPLEX ,0.6 ,(255 ,255 ,255 ),2 )
            cv2 .putText (frame ,f"Opacidad: {self.model_opacity:.2f}",(10 ,90 ),
            cv2 .FONT_HERSHEY_SIMPLEX ,0.6 ,(255 ,255 ,255 ),2 )


            cv2 .putText (frame ,"AZUL=Derecha (Camara)",(w -200 ,30 ),
            cv2 .FONT_HERSHEY_SIMPLEX ,0.4 ,(255 ,0 ,0 ),1 )
            cv2 .putText (frame ,"VERDE=Izquierda (Visual)",(w -200 ,50 ),
            cv2 .FONT_HERSHEY_SIMPLEX ,0.4 ,(0 ,255 ,0 ),1 )

            cv2 .imshow ("Hand Control",frame )
            cv2 .waitKey (1 )

    def process_right_hand (self ,hand_landmarks ,hand_x ,hand_y ,frame ):
        """Procesa la mano derecha para controles de cámara"""

        if self .last_right_hand_pos is not None :

            dx =(hand_x -self .last_right_hand_pos [0 ])*150
            dy =(hand_y -self .last_right_hand_pos [1 ])*150


            self .camera_rotation_y +=dx
            self .camera_rotation_x +=dy


        pinch_distance =self .calculate_pinch_distance (hand_landmarks )


        min_distance =0.02
        max_distance =0.15
        normalized_distance =max (0 ,min (1 ,(pinch_distance -min_distance )/(max_distance -min_distance )))
        target_distance =25.0 -(normalized_distance *20.0 )


        self .camera_distance +=(target_distance -self .camera_distance )*0.1
        self .camera_distance =max (2.0 ,min (50.0 ,self .camera_distance ))

        self .last_right_hand_pos =(hand_x ,hand_y )


        if self .show_camera :
            thumb_tip =hand_landmarks .landmark [4 ]
            index_tip =hand_landmarks .landmark [8 ]

            h ,w ,_ =frame .shape
            thumb_pos =(int (thumb_tip .x *w ),int (thumb_tip .y *h ))
            index_pos =(int (index_tip .x *w ),int (index_tip .y *h ))


            cv2 .line (frame ,thumb_pos ,index_pos ,(255 ,0 ,0 ),3 )

    def process_left_hand (self ,hand_landmarks ,hand_x ,hand_y ,frame ):
        """Procesa la mano izquierda para controles visuales"""

        pinch_distance =self .calculate_pinch_distance (hand_landmarks )


        if pinch_distance <0.05 :
            self .is_red_mode =True
            self .model_color =[1.0 ,0.0 ,0.0 ]
        else :
            self .is_red_mode =False
            self .model_color =[1.0 ,1.0 ,1.0 ]


        if self .last_left_hand_pos is not None :

            dx =abs (hand_x -self .last_left_hand_pos [0 ])


            if dx >0.02 :
                self .model_opacity -=dx *3.0
                self .model_opacity =max (0.1 ,min (1.0 ,self .model_opacity ))


        if self .last_left_hand_pos is not None :
            dx =abs (hand_x -self .last_left_hand_pos [0 ])
            if dx <0.01 :
                self .model_opacity +=0.02
                self .model_opacity =min (1.0 ,self .model_opacity )

        self .last_left_hand_pos =(hand_x ,hand_y )


        if self .show_camera :
            thumb_tip =hand_landmarks .landmark [4 ]
            index_tip =hand_landmarks .landmark [8 ]

            h ,w ,_ =frame .shape
            thumb_pos =(int (thumb_tip .x *w ),int (thumb_tip .y *h ))
            index_pos =(int (index_tip .x *w ),int (index_tip .y *h ))


            color =(0 ,0 ,255 )if pinch_distance <0.05 else (0 ,255 ,0 )
            cv2 .line (frame ,thumb_pos ,index_pos ,color ,3 )

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

    def render_model (self ):
        """Renderiza el modelo PLY con color y opacidad dinámicos"""
        if self .model .vertex_count >0 :

            glEnable (GL_BLEND )
            glBlendFunc (GL_SRC_ALPHA ,GL_ONE_MINUS_SRC_ALPHA )


            glColor4f (self .model_color [0 ],self .model_color [1 ],self .model_color [2 ],self .model_opacity )

            glEnableClientState (GL_VERTEX_ARRAY )
            glVertexPointer (3 ,GL_FLOAT ,0 ,self .model .vertices )

            glPointSize (2.0 )
            glDrawArrays (GL_POINTS ,0 ,self .model .vertex_count )

            glDisableClientState (GL_VERTEX_ARRAY )
            glDisable (GL_BLEND )

    def run (self ):
        """Bucle principal"""
        try :
            clock =pygame .time .Clock ()
            running =True

            print (" Visualizador Basteria con Control Dual de Manos iniciado")
            print (" Controles:")
            print ("\n MANO DERECHA (Cámara - AZUL):")
            print ("    Mover palma = Rotar modelo")
            print ("    Pinch = ALEJAR zoom")
            print ("   ️  Separar = ACERCAR zoom")
            print ("\n MANO IZQUIERDA (Visual - VERDE):")
            print ("    Pinch = Cambiar a color ROJO")
            print ("    Abrir = Cambiar a color BLANCO")
            print ("   ↔️  Mover lado a lado = Reducir opacidad")
            print ("    Quieta = Recuperar opacidad")
            print ("\n⌨️  Teclado:")
            print ("    C: Mostrar/Ocultar ventana de cámara")
            print ("    H: Activar/Desactivar control de manos")
            print ("   ️  Mouse: Rotar modelo (alternativo)")
            print ("    ESC: Salir")
            print (f"\n Mostrando {self.model.vertex_count:,} vértices de models/basteria2.ply")
            print (" Usa ambas manos frente a la cámara para control completo")

            while running :
                for event in pygame .event .get ():
                    if event .type ==pygame .QUIT :
                        running =False
                    elif event .type ==pygame .KEYDOWN :
                        if event .key ==pygame .K_ESCAPE :
                            running =False
                        elif event .key ==pygame .K_c :
                            self .show_camera =not self .show_camera
                            print (f" Cámara: {'Visible' if self.show_camera else 'Oculta'}")
                        elif event .key ==pygame .K_h :
                            self .hand_control_enabled =not self .hand_control_enabled
                            print (f" Control de manos: {'Activado' if self.hand_control_enabled else 'Desactivado'}")
                        elif event .key ==pygame .K_r :

                            self .camera_distance =15.0
                            self .camera_rotation_x =0.0
                            self .camera_rotation_y =0.0
                            print (" Cámara reiniciada")
                    elif event .type ==pygame .MOUSEWHEEL :

                        self .camera_distance =max (2.0 ,min (50.0 ,self .camera_distance -event .y ))


                self .process_hand_tracking ()


                self .handle_mouse_input ()


                glClear (GL_COLOR_BUFFER_BIT |GL_DEPTH_BUFFER_BIT )


                glLoadIdentity ()
                glTranslatef (0 ,0 ,-self .camera_distance )
                glRotatef (self .camera_rotation_x ,1 ,0 ,0 )
                glRotatef (self .camera_rotation_y ,0 ,1 ,0 )


                self .render_model ()


                pygame .display .flip ()
                clock .tick (60 )

        except Exception as e :
            print (f" Error durante la ejecución: {e}")
        finally :

            if hasattr (self ,'cap'):
                self .cap .release ()
            cv2 .destroyAllWindows ()
            pygame .quit ()
            print (" ¡Hasta luego!")

def main ():
    """Función principal"""
    try :
        viewer =BasteriaViewerMediaPipe ('models/basteria2.ply')
        viewer .run ()
    except Exception as e :
        print (f" Error al inicializar: {e}")
        print (" Asegúrate de que:")
        print ("   - models/basteria2.ply existe en el directorio")
        print ("   - La cámara esté conectada y disponible")
        print ("   - Estés usando Python 3.10 con MediaPipe instalado")

if __name__ =="__main__":
    main ()
