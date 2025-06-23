"""
Visualizador de Basteria PLY con Control Dual de Manos (MediaPipe)
- Mano derecha: Control de cámara (rotación y zoom con pinch)
- Mano izquierda: Efectos visuales (vibración, color y opacidad con pinch)
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
import collections


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


                vertices_raw =np .column_stack ([
                vertex_data ['x'],
                vertex_data ['y'],
                vertex_data ['z']
                ])


                self .vertices =vertices_raw .astype (np .float32 )


                if len (self .vertices )>0 :
                    center =np .mean (self .vertices ,axis =0 )
                    self .vertices -=center

                    max_coord =np .max (np .abs (self .vertices ))
                    if max_coord >0 :
                        scale_factor =8.0 /max_coord
                        self .vertices *=scale_factor

                    self .vertex_count =len (self .vertices )
                    print (f" Modelo procesado: {self.vertex_count} vértices")
                    return
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

class BacteriaModel :
    """Modelo para una única bacteria, que maneja la vibración de sus vértices."""
    def __init__ (self ,filename ):
        print (f" Cargando modelo de bacteria desde: {filename}")
        self .original_vertices ,self .vertex_count =self .load_bact (filename )

        if self .original_vertices is not None :
            self .transformed_vertices =np .copy (self .original_vertices )
            print (f" Bacteria cargada ({self.vertex_count} vértices).")
        else :
            self .transformed_vertices =None

    def load_bact (self ,filename ):
        """Carga un único modelo de bacteria desde un archivo PLY."""
        try :
            with open (filename ,'rb')as f :
                plydata =PlyData .read (f )
                vertices =np .column_stack ([plydata ['vertex']['x'],plydata ['vertex']['y'],plydata ['vertex']['z']])

                center =np .mean (vertices ,axis =0 )
                vertices -=center
                max_coord =np .max (np .abs (vertices ))
                if max_coord >0 :
                    vertices *=(7.0 /max_coord )

                return vertices .astype (np .float32 ),len (vertices )
        except Exception as e :
            print (f" Error cargando la bacteria {filename}: {e}")
            return None ,0

    def apply_vertex_shake (self ,shake_intensity ):
        """Aplica vibración a nivel de vértice."""
        if self .original_vertices is not None :
            if shake_intensity >0.01 :

                shake_strength =shake_intensity *0.3
                shake_offsets =(np .random .standard_normal (size =self .original_vertices .shape )*shake_strength ).astype (np .float32 )
                self .transformed_vertices =self .original_vertices +shake_offsets
            else :

                self .transformed_vertices =np .copy (self .original_vertices )

class ADNModel :
    """Modelo especializado para el ADN, que maneja dos hebras separadas desde archivos distintos."""
    def __init__ (self ,filename1 ,filename2 ):
        print (f" Cargando modelos de ADN: {filename1}, {filename2}")
        self .strand1_original =None
        self .strand2_original =None
        self .strand1_displaced =None
        self .strand2_displaced =None
        self .vertex_count1 =0
        self .vertex_count2 =0


        self .strand1_original ,self .vertex_count1 =self .load_strand (filename1 )
        self .strand2_original ,self .vertex_count2 =self .load_strand (filename2 )

        if self .strand1_original is not None and self .strand2_original is not None :

            self .strand1_displaced =np .copy (self .strand1_original )
            self .strand2_displaced =np .copy (self .strand2_original )
            print (f" ADN cargado: Hebra 1 ({self.vertex_count1} verts), Hebra 2 ({self.vertex_count2} verts)")

    def load_strand (self ,filename ):
        """Carga una única hebra desde un archivo PLY, la centra y la escala."""
        try :
            plydata =PlyData .read (filename )
            vertices =np .column_stack ([plydata ['vertex']['x'],plydata ['vertex']['y'],plydata ['vertex']['z']])


            center =np .mean (vertices ,axis =0 )
            vertices -=center
            max_coord =np .max (np .abs (vertices ))
            if max_coord >0 :
                vertices *=(10.0 /max_coord )

            return vertices .astype (np .float32 ),len (vertices )
        except Exception as e :
            print (f" Error cargando la hebra {filename}: {e}")
            return None ,0

    def separate_strands (self ,separation_factor ):
        """Desplaza las hebras a lo largo del eje X basado en el factor de separación."""
        if self .strand1_original is not None :

            separation_vector =np .array ([separation_factor *10.0 ,0 ,0 ],dtype =np .float32 )
            self .strand1_displaced =self .strand1_original -separation_vector
            self .strand2_displaced =self .strand2_original +separation_vector

class PCRModel :
    """Modelo para la simulación de PCR, que replica fragmentos."""
    def __init__ (self ,filename ):
        self .base_fragment ,self .vertex_count =self .load_fragment (filename )
        self .fragments =[]
        self .max_fragments =200
        self .fragment_lifespan =180

    def load_fragment (self ,filename ):
        """Carga el fragmento de ADN base."""
        try :
            plydata =PlyData .read (filename )
            vertices =np .column_stack ([plydata ['vertex']['x'],plydata ['vertex']['y'],plydata ['vertex']['z']])
            center =np .mean (vertices ,axis =0 )
            vertices -=center
            max_coord =np .max (np .abs (vertices ))
            if max_coord >0 :
                vertices *=(2.0 /max_coord )
            return vertices .astype (np .float32 ),len (vertices )
        except Exception as e :
            print (f" Error cargando fragmento de PCR {filename}: {e}")
            return None ,0

    def update (self ,hand_velocity ):
        """Actualiza la simulación: crea nuevos fragmentos y gestiona su tiempo de vida."""

        if hand_velocity >0.05 and len (self .fragments )<self .max_fragments :

            for _ in range (2 ):
                if len (self .fragments )<self .max_fragments :

                    x =(np .random .rand ()-0.5 )*20
                    y =(np .random .rand ()-0.5 )*20
                    z =(np .random .rand ()-0.5 )*20


                    angle =np .random .rand ()*360
                    axis =np .random .rand (3 )
                    axis /=np .linalg .norm (axis )

                    self .fragments .append ({'pos':[x ,y ,z ],'angle':angle ,'axis':axis ,'life':self .fragment_lifespan })



        decay_rate =10 if hand_velocity <0.01 else 1
        self .fragments =[f for f in self .fragments if f ['life']>0 ]
        for f in self .fragments :
            f ['life']-=decay_rate

    def update_fragments (self ,hand_still ):
        """Actualiza el estado de la simulación PCR, como el tiempo de vida de los fragmentos."""
        if self .base_fragment is not None :

            decay_rate =10 if hand_still else 1
            self .fragments =[f for f in self .fragments if f ['life']>0 ]
            for f in self .fragments :
                f ['life']-=decay_rate

class EnzymeModel :
    """Modelo para la enzima (polimerasa) y el fragmento de ADN."""
    def __init__ (self ,enzyme_file ,fragment_file ):
        print (f" Cargando modelo de enzima: {enzyme_file}")
        self .enzyme_model ,self .enzyme_vertex_count =self .load_model (enzyme_file ,scale =1.5 )

        print (f" Cargando modelo de fragmento: {fragment_file}")

        self .fragment_model ,self .fragment_vertex_count =self .load_model (fragment_file ,scale =4.0 )

        self .enzyme_position =np .array ([0 ,5 ,0 ],dtype =np .float32 )
        self .is_attached =False
        self .attachment_progress =0.0

    def load_model (self ,filename ,scale =1.0 ):
        """Carga un modelo PLY, lo centra y lo escala."""
        try :
            with open (filename ,'rb')as f :
                plydata =PlyData .read (f )
                vertices =np .column_stack ([plydata ['vertex']['x'],plydata ['vertex']['y'],plydata ['vertex']['z']])

                center =np .mean (vertices ,axis =0 )
                vertices -=center
                max_coord =np .max (np .abs (vertices ))
                if max_coord >0 :
                    vertices *=(scale /max_coord )

                return vertices .astype (np .float32 ),len (vertices )
        except Exception as e :
            print (f" Error cargando el modelo {filename}: {e}")
            return None ,0

    def attach_enzyme (self ,attachment_factor ):
        """Mueve la enzima hacia el fragmento de ADN. Se queda 'pegada' si el factor es alto."""
        if self .enzyme_model is not None :

            target_position =np .array ([0 ,1.0 ,1.0 ],dtype =np .float32 )


            start_position =np .array ([0 ,5 ,1.0 ],dtype =np .float32 )
            self .enzyme_position =(1 -attachment_factor )*start_position +attachment_factor *target_position


            self .attachment_progress =attachment_factor


            self .is_attached =attachment_factor >=0.99

class HelicaseModel:
    def __init__(self, filename):
        self.model, self.vertex_count = self.load_model(filename, scale=1.1)
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.angle = 0.0

    def load_model(self, filename, scale=1.0):
        try:
            plydata = PlyData.read(filename)
            vertices = np.column_stack([
                plydata['vertex']['x'],
                plydata['vertex']['y'],
                plydata['vertex']['z'],
            ])
            center = np.mean(vertices, axis=0)
            vertices -= center
            max_c = np.max(np.abs(vertices))
            if max_c > 0:
                vertices *= scale / max_c
            return vertices.astype(np.float32), len(vertices)
        except Exception:
            return None, 0

    def update(self, factor):
        # Move linearly along Z axis through the DNA strands.
        # factor 0 -> z=-4 (inicio), factor 1 -> z=+4 (extremo opuesto)
        z = -8 + 18 * factor
        self.position = np.array([0.0, 0.0, z], dtype=np.float32)

class BasteriaViewerMediaPipe :
    """Visualizador con controles duales de mano usando MediaPipe"""

    def __init__ (self ,ply_file ='models/basteria2.ply'):
        print (' Inicializando Visualizador Basteria con MediaPipe...')
        pygame .init ()


        self .screen_width ,self .screen_height =1920 ,1080
        self .fullscreen =False
        self .screen =pygame .display .set_mode ((self .screen_width ,self .screen_height ),DOUBLEBUF |OPENGL )
        pygame .display .set_caption (' Visualizador Basteria')
        self .setup_opengl ()


        self .camera_distance =15.0
        self .camera_rotation_x =0.0
        self .camera_rotation_y =0.0
        self .auto_rotation_speed =0.2


        print (' Inicializando MediaPipe...')
        self .hands =mp_hands .Hands (model_complexity =1 ,min_detection_confidence =0.7 ,min_tracking_confidence =0.7 ,max_num_hands =2 )
        print (' Inicializando cámara...')
        self .cap =cv2 .VideoCapture (0 )
        self .cap .set (cv2 .CAP_PROP_FRAME_WIDTH ,640 )
        self .cap .set (cv2 .CAP_PROP_FRAME_HEIGHT ,480 )


        self .hand_control_enabled =True
        self .show_camera =True
        self .hand_separation =0.0
        self .gesture_cooldown =0
        self .touch_threshold =0.06
        self .touch_gesture_start_time =None
        self .left_hand_history =collections .deque (maxlen =5 )
        self .left_hand_present_this_frame =False
        self .last_right_hand_pos =None
        self .last_left_hand_pos =None
        self .last_mouse_pos =None


        self .initialize_effects ()


        self .states =['BASTERIA','ADN','ENZYME','PCR']
        self .current_state_index =0
        self .state =self .states [self .current_state_index ]

        self .basteria_model =BacteriaModel ('models/basteria2.ply')
        self .adn_model =ADNModel ('models/adn1.ply','models/adn2.ply')
        self .enzyme_model =EnzymeModel ('models/polimerasa.ply','models/fragmentoadn.ply')
        self .pcr_model =PCRModel ('models/fragmentoadn.ply')
        self .helicase_model = HelicaseModel('models/helicasa.ply')

        print (' Inicialización completa')

    def setup_opengl (self ):
        """Configura OpenGL"""
        glEnable (GL_DEPTH_TEST )
        glDepthFunc (GL_LESS )



        w ,h =pygame .display .get_surface ().get_size ()
        glViewport (0 ,0 ,w ,h )

        glMatrixMode (GL_PROJECTION )
        glLoadIdentity ()


        aspect_ratio =w /h if h >0 else 1
        gluPerspective (45 ,aspect_ratio ,0.1 ,100.0 )
        glMatrixMode (GL_MODELVIEW )
        glClearColor (0.05 ,0.05 ,0.1 ,1.0 )

    def toggle_fullscreen (self ):
        """Alterna entre modo ventana y pantalla completa."""
        self .fullscreen =not self .fullscreen
        if self .fullscreen :
            self .screen =pygame .display .set_mode ((self .screen_width ,self .screen_height ),DOUBLEBUF |OPENGL |FULLSCREEN )
            print (f"️ Modo pantalla completa: {self.screen_width}x{self.screen_height}")
        else :
            self .screen =pygame .display .set_mode ((self .screen_width ,self .screen_height ),DOUBLEBUF |OPENGL )
            print (f" Modo ventana: {self.screen_width}x{self.screen_height}")


        self .setup_opengl ()

    def initialize_effects (self ):
        """Prepara las variables para los efectos visuales."""

        self .shake_intensity =0.0
        self .color_blend_factor =0.0
        self .model_opacity =1.0
        self .model_color =[1.0 ,1.0 ,1.0 ]
        print (" Efectos visuales inicializados.")

    def setup_models (self ):
        """Esta función ahora está vacía ya que los modelos se cargan en __init__."""

        pass

    def update_auto_rotation (self ):
        """Actualiza la rotación automática (siempre activa)"""
        self .camera_rotation_y +=self .auto_rotation_speed
        if self .camera_rotation_y >=360 :
            self .camera_rotation_y -=360

    def apply_shaking_effect (self ):
        """Aplica el efecto de sacudida al modelo de basteria."""


        pass

    def calculate_landmark_distance (self ,p1 ,p2 ):
        """Calcula la distancia euclidiana 3D entre dos landmarks."""
        return math .sqrt ((p1 .x -p2 .x )**2 +(p1 .y -p2 .y )**2 +(p1 .z -p2 .z )**2 )

    def is_fist (self ,hand_landmarks ):
        """Detecta si la mano está en un puño."""
        try :

            thumb_tip =hand_landmarks .landmark [mp_hands .HandLandmark .THUMB_TIP ]
            index_tip =hand_landmarks .landmark [mp_hands .HandLandmark .INDEX_FINGER_TIP ]
            middle_tip =hand_landmarks .landmark [mp_hands .HandLandmark .MIDDLE_FINGER_TIP ]
            ring_tip =hand_landmarks .landmark [mp_hands .HandLandmark .RING_FINGER_TIP ]
            pinky_tip =hand_landmarks .landmark [mp_hands .HandLandmark .PINKY_TIP ]


            wrist =hand_landmarks .landmark [mp_hands .HandLandmark .WRIST ]



            fist_threshold =self .calculate_landmark_distance (
            hand_landmarks .landmark [mp_hands .HandLandmark .INDEX_FINGER_MCP ],wrist
            )*0.8

            is_closed =(self .calculate_landmark_distance (index_tip ,wrist )<fist_threshold and
            self .calculate_landmark_distance (middle_tip ,wrist )<fist_threshold and
            self .calculate_landmark_distance (ring_tip ,wrist )<fist_threshold and
            self .calculate_landmark_distance (pinky_tip ,wrist )<fist_threshold )
            return is_closed
        except :
            return False

    def process_hand_tracking (self ):
        """Procesa la imagen de la cámara para detectar y analizar las manos."""
        self .left_hand_present_this_frame =False

        success ,frame =self .cap .read ()
        if not success :
            return


        frame =cv2 .flip (frame ,1 )

        image =cv2 .cvtColor (frame ,cv2 .COLOR_BGR2RGB )
        results =self .hands .process (image )
        image =cv2 .cvtColor (image ,cv2 .COLOR_RGB2BGR )

        left_hand_landmarks =None
        right_hand_landmarks =None
        left_hand_pos =None
        right_hand_pos =None

        if results .multi_hand_landmarks :
            for hand_landmarks ,handedness in zip (results .multi_hand_landmarks ,results .multi_handedness ):
                is_right_hand =handedness .classification [0 ].label =='Right'

                x_coords =[lm .x for lm in hand_landmarks .landmark ]
                y_coords =[lm .y for lm in hand_landmarks .landmark ]

                if is_right_hand :
                    right_hand_landmarks =hand_landmarks
                    right_hand_pos =(np .mean (x_coords ),np .mean (y_coords ))
                else :
                    left_hand_landmarks =hand_landmarks
                    left_hand_pos =(np .mean (x_coords ),np .mean (y_coords ))
                    self .left_hand_present_this_frame =True


            if self .gesture_cooldown ==0 :
                if left_hand_landmarks and right_hand_landmarks :

                    p1 =right_hand_landmarks .landmark [mp_hands .HandLandmark .INDEX_FINGER_TIP ]

                    p2 =left_hand_landmarks .landmark [mp_hands .HandLandmark .WRIST ]

                    touch_distance =self .calculate_landmark_distance (p1 ,p2 )
                    if touch_distance <self .touch_threshold :
                        self .cycle_state ()


            if self .state =='ADN':

                if left_hand_pos and right_hand_pos :

                    hand_dist =abs (right_hand_pos [0 ]-left_hand_pos [0 ])


                    self .hand_separation =np .interp (hand_dist ,[0.25 ,0.8 ],[0.0 ,1.0 ])
                else :

                    self .hand_separation =0.0

                # update helicase
                self .helicase_model.update(self .hand_separation)

            if right_hand_landmarks :
                self .process_right_hand (right_hand_landmarks ,right_hand_pos [0 ],right_hand_pos [1 ],image )
            if left_hand_landmarks :
                self .process_left_hand (left_hand_landmarks ,left_hand_pos [0 ],left_hand_pos [1 ],image )


        if results .multi_hand_landmarks and self .show_camera :
            for hand_landmarks ,handedness in zip (results .multi_hand_landmarks ,results .multi_handedness ):
                color =(255 ,0 ,0 )if handedness .classification [0 ].label =='Right'else (0 ,255 ,0 )
                mp_drawing .draw_landmarks (image ,hand_landmarks ,mp_hands .HAND_CONNECTIONS ,
                landmark_drawing_spec =mp_drawing .DrawingSpec (color =color ,thickness =2 ,circle_radius =4 ))

        if self .show_camera :
            if self .state =='ADN':
                # No se muestra texto: solo landmarks
                pass

            # Sin overlay de texto de zoom

        cv2 .imshow ('Hand Tracking',image )

    def get_hand_angle (self ,hand_landmarks ):
        """Calcula el ángulo de la mano usando la muñeca y la base del dedo medio."""
        wrist =hand_landmarks .landmark [0 ]
        mcp =hand_landmarks .landmark [9 ]
        angle =math .atan2 (mcp .y -wrist .y ,mcp .x -wrist .x )
        return math .degrees (angle )

    def process_right_hand (self ,hand_landmarks ,hand_x ,hand_y ,frame ):
        """Procesa la mano derecha para controles de cámara y ciclado de niveles."""


        if self .gesture_cooldown >0 :
            self .gesture_cooldown -=1
            return



        if self .last_right_hand_pos :
            dx =(hand_x -self .last_right_hand_pos [0 ])*150
            dy =(hand_y -self .last_right_hand_pos [1 ])*150
            self .camera_rotation_y +=dx
            self .camera_rotation_x +=dy
        self .last_right_hand_pos =(hand_x ,hand_y )


        pinch_distance =self .calculate_landmark_distance (hand_landmarks .landmark [4 ],hand_landmarks .landmark [8 ])

        min_dist =0.02
        max_dist =0.20


        normalized_distance =max (0 ,min (1 ,(pinch_distance -min_dist )/(max_dist -min_dist )))


        target_distance =5.0 +(normalized_distance *20.0 )


        self .camera_distance +=(target_distance -self .camera_distance )*0.4
        self .camera_distance =max (2.0 ,min (50.0 ,self .camera_distance ))


        if self .show_camera :
            thumb_tip =hand_landmarks .landmark [4 ]
            index_tip =hand_landmarks .landmark [8 ]

            h ,w ,_ =frame .shape
            thumb_pos =(int (thumb_tip .x *w ),int (thumb_tip .y *h ))
            index_pos =(int (index_tip .x *w ),int (index_tip .y *h ))


            line_blue =int (255 *normalized_distance )
            line_green =int (255 *(1 -normalized_distance ))
            color =(line_blue ,line_green ,0 )
            cv2 .line (frame ,thumb_pos ,index_pos ,color ,3 )

    def cycle_state (self ):
        """Cicla al siguiente estado en la lista de estados."""
        self .current_state_index =(self .current_state_index +1 )%len (self .states )
        self .state =self .states [self .current_state_index ]
        print (f" Gesto Detectado! Cambiando a modo {self.state}.")


        if self .state =='ADN'and self .adn_model is None :
            self .adn_model =ADNModel ('models/adn1.ply','models/adn2.ply')
        elif self .state =='PCR'and self .pcr_model is None :
            self .pcr_model =PCRModel ('models/fragmentoadn.ply')

        self .gesture_cooldown =45


        if self .enzyme_model :
            self .enzyme_model .is_attached =False
            self .enzyme_model .attachment_progress =0.0
            self .enzyme_model .enzyme_position =np .array ([0 ,5 ,0 ],dtype =np .float32 )

            # Rota la cámara 30° hacia abajo al entrar en ENZYME
            self .camera_rotation_x = 30.0  # mirar ligeramente desde arriba

    def process_left_hand (self ,hand_landmarks ,hand_x ,hand_y ,frame ):
        """Procesa los landmarks de la mano izquierda para controlar efectos."""

        if self .state =='PCR'and self .pcr_model :
            p1 =hand_landmarks .landmark [mp_hands .HandLandmark .WRIST ]
            self .left_hand_history .append ({'pos':(p1 .x ,p1 .y ),'time':time .time ()})

            hand_velocity =0
            if len (self .left_hand_history )>2 :
                start =self .left_hand_history [0 ]
                end =self .left_hand_history [-1 ]
                delta_time =end ['time']-start ['time']
                dist =math .sqrt ((end ['pos'][0 ]-start ['pos'][0 ])**2 +(end ['pos'][1 ]-start ['pos'][1 ])**2 )
                if delta_time >0 :
                    hand_velocity =dist /delta_time
            self .pcr_model .update (hand_velocity )


        if self .state =='BASTERIA':
            pinch_distance =self .calculate_landmark_distance (hand_landmarks .landmark [4 ],hand_landmarks .landmark [8 ])


            min_distance =0.015
            max_distance =0.1

            normalized_factor =0.0
            if pinch_distance <min_distance :
                normalized_factor =1.0
            elif pinch_distance <max_distance :
                normalized_factor =1.0 -((pinch_distance -min_distance )/(max_distance -min_distance ))

            self .shake_intensity =normalized_factor
            self .color_blend_factor =normalized_factor
            self .model_opacity =1.0 -(normalized_factor *0.6 )

            white_color =np .array ([1.0 ,1.0 ,1.0 ])
            red_color =np .array ([1.0 ,0.0 ,0.0 ])
            self .model_color =((1.0 -self .color_blend_factor )*white_color +self .color_blend_factor *red_color ).tolist ()

            if self .show_camera :
                thumb_tip =hand_landmarks .landmark [4 ]
                index_tip =hand_landmarks .landmark [8 ]

                h ,w ,_ =frame .shape
                thumb_pos =(int (thumb_tip .x *w ),int (thumb_tip .y *h ))
                index_pos =(int (index_tip .x *w ),int (index_tip .y *h ))

                line_red =255
                line_green =int ((1.0 -self .color_blend_factor )*255 )
                line_blue =int ((1.0 -self .color_blend_factor )*255 )
                color =(line_blue ,line_green ,line_red )
                cv2 .line (frame ,thumb_pos ,index_pos ,color ,3 )


        if self .state =='ADN':

            pinch_dist =self .calculate_landmark_distance (hand_landmarks .landmark [4 ],hand_landmarks .landmark [8 ])
            separation_factor =np .clip ((pinch_dist -0.02 )/0.15 ,0 ,1 )
            self .adn_model .separate_strands (separation_factor )

        elif self .state =='ENZYME':
            if self .enzyme_model :

                pinch_dist =self .calculate_landmark_distance (hand_landmarks .landmark [4 ],hand_landmarks .landmark [8 ])



                min_dist =0.02
                max_dist =0.12
                normalized =np .clip ((pinch_dist -min_dist )/(max_dist -min_dist ),0.0 ,1.0 )


                attachment_factor =1.0 -normalized

                self .enzyme_model .attach_enzyme (attachment_factor )


                if self .show_camera :
                    thumb_tip =hand_landmarks .landmark [4 ]
                    index_tip =hand_landmarks .landmark [8 ]
                    h ,w ,_ =frame .shape
                    thumb_pos =(int (thumb_tip .x *w ),int (thumb_tip .y *h ))
                    index_pos =(int (index_tip .x *w ),int (index_tip .y *h ))


                    red =int (255 *(1 -attachment_factor ))
                    green =int (255 *attachment_factor )
                    cv2 .line (frame ,thumb_pos ,index_pos ,(0 ,green ,red ),3 )  # solo la línea como feedback visual sin texto

    def handle_mouse_input (self ):
        """Maneja la entrada del mouse para control de cámara alternativo."""

        mouse_buttons =pygame .mouse .get_pressed ()
        if mouse_buttons [0 ]:
            if self .last_mouse_pos :
                dx ,dy =pygame .mouse .get_rel ()
                self .camera_rotation_y +=dx *0.5
                self .camera_rotation_x +=dy *0.5
        self .last_mouse_pos =pygame .mouse .get_pos ()if mouse_buttons [0 ]else None

    def render_basteria (self ):
        """Renderiza la única instancia de la basteria."""
        if self .basteria_model and self .basteria_model .vertex_count >0 :
            glEnable (GL_BLEND )
            glBlendFunc (GL_SRC_ALPHA ,GL_ONE_MINUS_SRC_ALPHA )
            glEnableClientState (GL_VERTEX_ARRAY )
            glPointSize (2.0 )


            glColor4f (self .model_color [0 ],self .model_color [1 ],self .model_color [2 ],self .model_opacity )
            glVertexPointer (3 ,GL_FLOAT ,0 ,self .basteria_model .transformed_vertices )
            glDrawArrays (GL_POINTS ,0 ,self .basteria_model .vertex_count )

            glDisableClientState (GL_VERTEX_ARRAY )
            glDisable (GL_BLEND )

    def render_adn (self ):
        """Renderiza el modelo de ADN con dos hebras de colores distintos."""
        if self .adn_model and self .adn_model .vertex_count1 >0 :
            glEnableClientState (GL_VERTEX_ARRAY )
            glPointSize (2.0 )


            glColor3f (0.0 ,1.0 ,1.0 )
            glVertexPointer (3 ,GL_FLOAT ,0 ,self .adn_model .strand1_displaced )
            glDrawArrays (GL_POINTS ,0 ,self .adn_model .vertex_count1 )


            glColor3f (1.0 ,0.0 ,1.0 )
            glVertexPointer (3 ,GL_FLOAT ,0 ,self .adn_model .strand2_displaced )
            glDrawArrays (GL_POINTS ,0 ,self .adn_model .vertex_count2 )

            glDisableClientState (GL_VERTEX_ARRAY )

    def render_enzyme (self ):
        """Renderiza la enzima y el fragmento de ADN."""
        if self .enzyme_model :
            glEnableClientState (GL_VERTEX_ARRAY )
            glPointSize (2.0 )


            glPushMatrix ()

            glRotatef (-90 ,1 ,0 ,0 )
            glColor3f (0.2 ,0.5 ,1.0 )
            glVertexPointer (3 ,GL_FLOAT ,0 ,self .enzyme_model .fragment_model )
            glDrawArrays (GL_POINTS ,0 ,self .enzyme_model .fragment_vertex_count )
            glPopMatrix ()


            glPushMatrix ()
            glTranslatef (self .enzyme_model .enzyme_position [0 ],
            self .enzyme_model .enzyme_position [1 ],
            self .enzyme_model .enzyme_position [2 ])

            glRotatef (-90 ,1 ,0 ,0 )


            progress =self .enzyme_model .attachment_progress
            base_color =np .array ([1.0 ,1.0 ,1.0 ])
            attached_color =np .array ([0.2 ,1.0 ,0.5 ])
            color =(1 -progress )*base_color +progress *attached_color
            glColor3f (color [0 ],color [1 ],color [2 ])

            glVertexPointer (3 ,GL_FLOAT ,0 ,self .enzyme_model .enzyme_model )
            glDrawArrays (GL_POINTS ,0 ,self .enzyme_model .enzyme_vertex_count )
            glPopMatrix ()

            glDisableClientState (GL_VERTEX_ARRAY )

    def render_pcr (self ):
        """Renderiza los fragmentos de la simulación de PCR."""
        if self .pcr_model and self .pcr_model .base_fragment is not None :
            glEnableClientState (GL_VERTEX_ARRAY )
            glPointSize (1.5 )
            glVertexPointer (3 ,GL_FLOAT ,0 ,self .pcr_model .base_fragment )

            for fragment in self .pcr_model .fragments :
                glPushMatrix ()

                glTranslatef (fragment ['pos'][0 ],fragment ['pos'][1 ],fragment ['pos'][2 ])
                glRotatef (fragment ['angle'],fragment ['axis'][0 ],fragment ['axis'][1 ],fragment ['axis'][2 ])


                life_ratio =fragment ['life']/self .pcr_model .fragment_lifespan
                glColor3f (life_ratio ,0.2 ,1.0 -life_ratio )

                glDrawArrays (GL_POINTS ,0 ,self .pcr_model .vertex_count )
                glPopMatrix ()

            glDisableClientState (GL_VERTEX_ARRAY )

    def update_pcr (self ):
        """Actualiza el estado de la simulación PCR, como el tiempo de vida de los fragmentos."""
        if self .pcr_model :

            hand_still =not self .left_hand_present_this_frame
            self .pcr_model .update_fragments (hand_still )

    def change_state (self ):
        """Dispara el cambio de estado y actualiza los modelos necesarios."""
        self .current_state_index =(self .current_state_index +1 )%len (self .states )
        self .state =self .states [self .current_state_index ]
        print (f" Gesto Detectado! Cambiando a modo {self.state}.")


        self .touch_gesture_start_time =None

    def render_helicase(self):
        if self.helicase_model and self.helicase_model.vertex_count > 0:
            glEnableClientState(GL_VERTEX_ARRAY)
            glPointSize(3.0)
            glPushMatrix()
            glTranslatef(*self.helicase_model.position)
            glColor3f(0.2,1.0,0.5)
            glVertexPointer(3, GL_FLOAT, 0, self.helicase_model.model)
            glDrawArrays(GL_POINTS, 0, self.helicase_model.vertex_count)
            glPopMatrix()
            glDisableClientState(GL_VERTEX_ARRAY)

    def run (self ):
        """Bucle principal"""
        try :
            clock =pygame .time .Clock ()
            running =True

            print (" Visualizador Basteria con Control Dual de Manos iniciado")
            print (" Controles:")
            print ("\n MANO DERECHA (Cámara - AZUL):")
            print ("    Mover palma = Rotar modelo")
            print ("    Pinch = Controlar zoom")
            print ("\n MANO IZQUIERDA (Control de Efectos):")
            print ("   (Modo BACTERIA)  Juntar dedos = VIBRACIÓN + ROJO + TRANSPARENCIA")
            print ("   (Modo BACTERIA)  Separar dedos = NORMAL + BLANCO + OPACO")
            print ("\n GESTOS ADICIONALES:")
            print ("   (Todos los modos)  Toca tu palma izquierda con el índice derecho para ciclar de nivel")
            print ("   (Modo ADN)  Manos separadas/juntas = Separar/Unir hebras de ADN")
            print ("   (Modo PCR)  Mueve la mano izquierda para replicar fragmentos de ADN")
            print ("\n⌨️  Teclado:")
            print ("    C: Mostrar/Ocultar ventana de cámara")
            print ("    H: Activar/Desactivar control de manos")
            print ("    A: Cambiar velocidad rotación automática")
            print ("    R: Reiniciar posición de cámara")
            print ("   ️ F: Toggle pantalla completa")
            print ("   ️  Mouse: Rotar modelo (alternativo)")
            print ("    ESC: Salir")
            print (f"\n Mostrando {self.basteria_model.vertex_count:,} vértices de models/basteria2.ply")

            while running :
                for event in pygame .event .get ():
                    if event .type ==pygame .QUIT :
                        running =False
                    elif event .type ==pygame .KEYDOWN :
                        if event .key ==pygame .K_ESCAPE :
                            running =False
                        elif event .key ==pygame .K_c :
                            self .show_camera =not self .show_camera
                        elif event .key ==pygame .K_h :
                            self .hand_control_enabled =not self .hand_control_enabled
                        elif event .key ==pygame .K_r :
                            self .camera_distance =15.0
                            self .camera_rotation_x =0.0
                            self .camera_rotation_y =0.0
                            self .model_opacity =1.0
                        elif event .key ==pygame .K_a :
                            speeds =[0.1 ,0.2 ,0.5 ,1.0 ]
                            current_index =speeds .index (self .auto_rotation_speed )if self .auto_rotation_speed in speeds else 1
                            self .auto_rotation_speed =speeds [(current_index +1 )%len (speeds )]
                        elif event .key ==pygame .K_f :
                            self .toggle_fullscreen ()
                    elif event .type ==pygame .MOUSEWHEEL :
                        self .camera_distance =max (2.0 ,min (50.0 ,self .camera_distance -event .y ))
                    elif event .type ==pygame .VIDEORESIZE :
                        self .setup_opengl ()


                self .process_hand_tracking ()
                self .handle_mouse_input ()
                self .update_auto_rotation ()


                if self .state =='BASTERIA'and self .basteria_model :
                    self .basteria_model .apply_vertex_shake (self .shake_intensity )
                elif self .state =='ADN'and self .adn_model :
                    self .adn_model .separate_strands (self .hand_separation )
                elif self .state =='ENZYME'and self .enzyme_model :

                    pass
                elif self .state =='PCR'and self .pcr_model :
                    self .update_pcr ()

                glClear (GL_COLOR_BUFFER_BIT |GL_DEPTH_BUFFER_BIT )
                glLoadIdentity ()
                glTranslatef (0 ,0 ,-self .camera_distance )
                glRotatef (self .camera_rotation_x ,1 ,0 ,0 )
                glRotatef (self .camera_rotation_y ,0 ,1 ,0 )

                if self .state =='BASTERIA':
                    self .render_basteria ()
                elif self .state =='ADN':
                    self .render_adn ()
                    self .render_helicase()
                elif self .state =='ENZYME':
                    self .render_enzyme ()
                elif self .state =='PCR':
                    self .render_pcr ()

                pygame .display .flip ()
                clock .tick (60 )

        except Exception as e :
            print (f" Error durante la ejecución: {e}")
            import traceback
            traceback .print_exc ()
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
        import traceback
        traceback .print_exc ()

if __name__ =="__main__":
    main ()
