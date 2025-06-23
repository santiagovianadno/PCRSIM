
"""
PCR Camera Simulation - Simulación con cámara usando basteria.ply
Desnaturalización interactiva de células con detección de manos
"""

print (" Iniciando PCR Camera Simulation...")

import sys
try :
    print ('Importando pygame...')
    import pygame
    print ('pygame importado ')

    print ('Importando cv2...')
    import cv2
    print ('cv2 importado ')

    print ('Importando mediapipe...')
    import mediapipe as mp
    print ('mediapipe importado ')

    print ('Importando numpy...')
    import numpy as np
    print ('numpy importado ')

    print ('Importando os, math, random...')
    import os
    import math
    import random
    print ('os, math, random importados ')

    print ('Importando typing...')
    from typing import List ,Tuple ,Optional
    print ('typing importado ')

    print ('Importando OpenGL...')
    from OpenGL .GL import *
    from OpenGL .GLU import *
    print ('OpenGL importado ')

    print ('Importando plyfile...')
    from plyfile import PlyData
    print ('plyfile importado ')

    print (' Todas las importaciones exitosas')

except Exception as e :
    print (f' Error en importaciones: {e}')
    import traceback
    traceback .print_exc ()
    sys .exit (1 )


print ('Configurando MediaPipe...')
mp_hands =mp .solutions .hands
mp_drawing =mp .solutions .drawing_utils
mp_drawing_styles =mp .solutions .drawing_styles
print ('MediaPipe configurado ')

class BasteriaCell :
    """Célula basada en el modelo basteria.ply"""

    def __init__ (self ,x :float ,y :float ,z :float ):
        self .x =x
        self .y =y
        self .z =z
        self .original_x =x
        self .original_y =y
        self .original_z =z
        self .temperature =25.0
        self .denaturation_level =0.0
        self .energy =100.0
        self .active =True
        self .color =(0.2 ,0.8 ,0.2 )
        self .size =random .uniform (0.8 ,1.2 )
        self .animation_phase =random .uniform (0 ,2 *math .pi )
        self .rotation =np .array ([0.0 ,0.0 ,0.0 ])
        self .rotation_speed =np .random .uniform (0.5 ,2.0 ,3 )

    def update (self ,dt :float ,hand_positions :List [Tuple [float ,float ,float ]]):
        """Actualiza el estado de la célula"""

        pass

class BasteriaPLYModel :
    """Modelo PLY para las células basteria"""

    def __init__ (self ,filename :str ):
        self .vertices =[]
        self .normals =[]
        self .colors =[]
        self .indices =[]
        self .center =np .array ([0.0 ,0.0 ,0.0 ])
        self .load_ply (filename )

    def load_ply (self ,filename :str ):
        """Carga el archivo PLY de basteria"""
        try :
            print (f"Intentando cargar {filename}...")
            plydata =PlyData .read (filename )
            print (f"PLY data leído, elementos: {list(plydata.elements)}")

            vertex_data =plydata ['vertex']
            print (f"Vertex data obtenido, tipo: {type(vertex_data)}")
            print (f"Propiedades disponibles: {[prop.name for prop in vertex_data.properties]}")


            prop_names =[prop .name for prop in vertex_data .properties ]
            if 'x'in prop_names and 'y'in prop_names and 'z'in prop_names :
                self .vertices =np .column_stack ([
                vertex_data ['x'],
                vertex_data ['y'],
                vertex_data ['z']
                ])
                print (f"Vértices extraídos: {len(self.vertices)}")


            if 'nx'in prop_names and 'ny'in prop_names and 'nz'in prop_names :
                self .normals =np .column_stack ([
                vertex_data ['nx'],
                vertex_data ['ny'],
                vertex_data ['nz']
                ])
                print (f"Normales extraídas: {len(self.normals)}")


            if 'red'in prop_names and 'green'in prop_names and 'blue'in prop_names :
                self .colors =np .column_stack ([
                vertex_data ['red']/255.0 ,
                vertex_data ['green']/255.0 ,
                vertex_data ['blue']/255.0
                ])
                print (f"Colores extraídos: {len(self.colors)}")
            else :

                self .colors =np .full ((len (self .vertices ),3 ),[1.0 ,1.0 ,1.0 ])
                print ("Usando color blanco neutro")


            if 'face'in plydata :
                face_data =plydata ['face']
                face_prop_names =[prop .name for prop in face_data .properties ]
                print (f"Propiedades de caras: {face_prop_names}")

                if 'vertex_indices'in face_prop_names :
                    self .indices =np .array ([list (face ['vertex_indices'])for face in face_data ])
                    print (f"Índices de caras extraídos: {len(self.indices)}")
                elif 'vertex_index'in face_prop_names :
                    self .indices =np .array ([list (face ['vertex_index'])for face in face_data ])
                    print (f"Índices de caras extraídos (vertex_index): {len(self.indices)}")


            if len (self .vertices )>0 :
                self .center =np .mean (self .vertices ,axis =0 )
                self .vertices -=self .center
                print (f"Modelo centrado en: {self.center}")

            print (f" Modelo basteria.ply cargado: {len(self.vertices)} vértices, {len(self.indices)} caras")

        except Exception as e :
            print (f" Error cargando basteria.ply: {e}")
            import traceback
            traceback .print_exc ()
            print ("Usando geometría por defecto...")
            self .create_default_geometry ()

    def create_default_geometry (self ):
        """Crea geometría por defecto si no se puede cargar el PLY"""

        radius =1.0
        segments =16

        vertices =[]
        normals =[]
        colors =[]
        indices =[]

        for i in range (segments +1 ):
            lat =math .pi *(-0.5 +float (i )/segments )
            for j in range (segments ):
                lon =2 *math .pi *float (j )/segments

                x =radius *math .cos (lat )*math .cos (lon )
                y =radius *math .cos (lat )*math .sin (lon )
                z =radius *math .sin (lat )

                vertices .append ([x ,y ,z ])
                normals .append ([x /radius ,y /radius ,z /radius ])
                colors .append ([0.2 ,0.8 ,0.2 ])

        for i in range (segments ):
            for j in range (segments ):
                first =i *segments +j
                second =first +segments
                third =first +1
                fourth =second +1

                if i !=0 :
                    indices .extend ([first ,second ,third ])
                if i !=segments -1 :
                    indices .extend ([second ,fourth ,third ])

        self .vertices =np .array (vertices )
        self .normals =np .array (normals )
        self .colors =np .array (colors )
        self .indices =np .array (indices )
        self .center =np .array ([0.0 ,0.0 ,0.0 ])

class PCRCameraSimulation :
    """Simulación de PCR con cámara y desnaturalización interactiva"""

    def __init__ (self ,width :int =1280 ,height :int =720 ):
        print ('Inicializando pygame...')
        pygame .init ()
        print ('pygame inicializado')
        self .width =width
        self .height =height
        print ('Creando ventana...')
        self .screen =pygame .display .set_mode ((width ,height ),pygame .OPENGL |pygame .DOUBLEBUF )
        pygame .display .set_caption ("PCR Camera - Desnaturalización Interactiva")
        print ('Ventana creada')
        print ('Configurando OpenGL...')
        glEnable (GL_DEPTH_TEST )
        glEnable (GL_BLEND )
        glBlendFunc (GL_SRC_ALPHA ,GL_ONE_MINUS_SRC_ALPHA )
        glClearColor (0.0 ,0.0 ,0.1 ,1.0 )
        glEnable (GL_LIGHTING )
        glEnable (GL_LIGHT0 )
        glEnable (GL_COLOR_MATERIAL )
        print ('OpenGL configurado')
        self .camera_distance =15.0
        self .camera_rotation_x =0.0
        self .camera_rotation_y =0.0
        print ('Generando células...')
        self .cells :List [BasteriaCell ]=[]
        self .generate_cells (1 )
        print ('Células generadas')
        print ('Cargando modelo PLY...')
        self .basteria_model =BasteriaPLYModel ("basteria.ply")
        print ('Modelo PLY cargado')
        print ('Inicializando cámara...')
        self .cap =cv2 .VideoCapture (0 )
        print ('Inicializando MediaPipe Hands...')
        self .hands =mp_hands .Hands (
        model_complexity =1 ,
        min_detection_confidence =0.7 ,
        min_tracking_confidence =0.7 ,
        max_num_hands =2
        )
        print ('MediaPipe Hands inicializado')
        self .show_camera =True
        self .paused =False
        self .stats ={
        'total_cells':len (self .cells ),
        'denatured_cells':0 ,
        'avg_temperature':25.0
        }
        print ('Inicialización completa')

    def generate_cells (self ,count :int ):
        """Genera células basteria aleatorias"""
        for _ in range (count ):
            x =random .uniform (-8 ,8 )
            y =random .uniform (-4 ,4 )
            z =random .uniform (-5 ,5 )
            self .cells .append (BasteriaCell (x ,y ,z ))

    def handle_events (self ):
        """Maneja eventos de pygame"""
        for event in pygame .event .get ():
            if event .type ==pygame .QUIT :
                return False
            elif event .type ==pygame .KEYDOWN :
                if event .key ==pygame .K_ESCAPE :
                    return False
                elif event .key ==pygame .K_c :
                    self .show_camera =not self .show_camera
                elif event .key ==pygame .K_p :
                    self .paused =not self .paused
                elif event .key ==pygame .K_r :
                    self .reset_simulation ()
            elif event .type ==pygame .MOUSEMOTION :
                if event .buttons [0 ]:
                    self .camera_rotation_y +=event .rel [0 ]*0.01
                    self .camera_rotation_x +=event .rel [1 ]*0.01
            elif event .type ==pygame .MOUSEBUTTONDOWN :
                if event .button ==4 :
                    self .camera_distance =max (5.0 ,self .camera_distance -1.0 )
                elif event .button ==5 :
                    self .camera_distance =min (30.0 ,self .camera_distance +1.0 )

        return True

    def reset_simulation (self ):
        """Reinicia la simulación"""
        for cell in self .cells :
            cell .denaturation_level =0.0
            cell .temperature =25.0
            cell .energy =100.0
            cell .active =True
            cell .x =cell .original_x
            cell .y =cell .original_y
            cell .z =cell .original_z

    def process_hand_tracking (self ):
        """Procesa el tracking de manos"""
        ret ,frame =self .cap .read ()
        if not ret :
            return []

        frame =cv2 .flip (frame ,1 )
        rgb_frame =cv2 .cvtColor (frame ,cv2 .COLOR_BGR2RGB )
        results =self .hands .process (rgb_frame )

        hand_positions =[]

        if results .multi_hand_landmarks :
            for hand_landmarks in results .multi_hand_landmarks :

                palm =hand_landmarks .landmark [9 ]


                x =(palm .x -0.5 )*20
                y =(0.5 -palm .y )*10
                z =palm .z *15

                hand_positions .append ((x ,y ,z ))


                if self .show_camera :
                    mp_drawing .draw_landmarks (
                    frame ,hand_landmarks ,mp_hands .HAND_CONNECTIONS ,
                    mp_drawing_styles .get_default_hand_landmarks_style (),
                    mp_drawing_styles .get_default_hand_connections_style ()
                    )

        if self .show_camera :

            small_frame =cv2 .resize (frame ,(320 ,240 ))
            frame_surface =pygame .surfarray .make_surface (small_frame .swapaxes (0 ,1 ))
            self .screen .blit (frame_surface ,(10 ,10 ))

        return hand_positions

    def update (self ,dt :float ):
        """Actualiza la simulación"""
        if self .paused :
            return


        hand_positions =self .process_hand_tracking ()


        denatured_count =0
        total_temp =0.0

        for cell in self .cells :
            cell .update (dt ,hand_positions )

            if cell .denaturation_level >0.8 :
                denatured_count +=1
            total_temp +=cell .temperature


        self .stats ['denatured_cells']=denatured_count
        if len (self .cells )>0 :
            self .stats ['avg_temperature']=total_temp /len (self .cells )

    def render_cell (self ,cell :BasteriaCell ):
        """Renderiza una célula individual"""
        glPushMatrix ()
        glTranslatef (cell .x ,cell .y ,cell .z )
        glScalef (cell .size ,cell .size ,cell .size )


        glColor3f (1.0 ,1.0 ,1.0 )
        self .render_ply_model ()

        glPopMatrix ()

    def render_ply_model (self ):
        """Renderiza el modelo PLY como puntos (más rápido para modelos pesados)"""

        glEnableClientState (GL_VERTEX_ARRAY )
        glEnableClientState (GL_COLOR_ARRAY )

        glVertexPointer (3 ,GL_FLOAT ,0 ,self .basteria_model .vertices )
        glColorPointer (3 ,GL_FLOAT ,0 ,self .basteria_model .colors )

        glPointSize (2.0 )
        glDrawArrays (GL_POINTS ,0 ,len (self .basteria_model .vertices ))

        glDisableClientState (GL_VERTEX_ARRAY )
        glDisableClientState (GL_COLOR_ARRAY )
            glDisableClientState (GL_VERTEX_ARRAY )
            glDisableClientState (GL_COLOR_ARRAY )

    def render_cells (self ):
        """Renderiza todas las células"""
        for cell in self .cells :
            self .render_cell (cell )

    def render_ui (self ):
        """Renderiza la interfaz de usuario"""
        glMatrixMode (GL_PROJECTION )
        glPushMatrix ()
        glLoadIdentity ()
        gluOrtho2D (0 ,self .width ,0 ,self .height )

        glMatrixMode (GL_MODELVIEW )
        glPushMatrix ()
        glLoadIdentity ()
        glDisable (GL_DEPTH_TEST )

        font =pygame .font .Font (None ,36 )
        small_font =pygame .font .Font (None ,24 )


        texts =[
        f"Células Basteria: {self.stats['total_cells']}",
        f"Modelo PLY: {len(self.basteria_model.vertices)} vértices",
        f"Cámara: {'Activa' if self.show_camera else 'Oculta'}"
        ]

        for i ,text in enumerate (texts ):
            surface =font .render (text ,True ,(255 ,255 ,255 ))
            self .screen .blit (surface ,(10 ,self .height -100 +i *30 ))


        controls =[
        "C: Mostrar/Ocultar cámara",
        "Mouse: Rotar cámara",
        "Scroll: Zoom",
        "ESC: Salir"
        ]

        for i ,control in enumerate (controls ):
            surface =small_font .render (control ,True ,(200 ,200 ,200 ))
            self .screen .blit (surface ,(self .width -300 ,10 +i *20 ))


        glEnable (GL_DEPTH_TEST )
        glMatrixMode (GL_PROJECTION )
        glPopMatrix ()
        glMatrixMode (GL_MODELVIEW )
        glPopMatrix ()

    def render (self ):
        """Renderiza la escena completa"""
        glClear (GL_COLOR_BUFFER_BIT |GL_DEPTH_BUFFER_BIT )


        glMatrixMode (GL_PROJECTION )
        glLoadIdentity ()
        gluPerspective (45 ,self .width /self .height ,0.1 ,100.0 )

        glMatrixMode (GL_MODELVIEW )
        glLoadIdentity ()
        glTranslatef (0.0 ,0.0 ,-self .camera_distance )
        glRotatef (self .camera_rotation_x ,1.0 ,0.0 ,0.0 )
        glRotatef (self .camera_rotation_y ,0.0 ,1.0 ,0.0 )


        self .render_cells ()


        self .render_ui ()

        pygame .display .flip ()

    def run (self ):
        """Bucle principal de la aplicación"""
        try :
            clock =pygame .time .Clock ()
            running =True

            print (" Visualizador de Células Basteria")
            print (" Controles:")
            print ("   - C: Mostrar/Ocultar cámara")
            print ("   - Mouse: Rotar cámara")
            print ("   - Scroll: Zoom")
            print ("   - ESC: Salir")
            print (f"\n Mostrando {len(self.cells)} células usando tu modelo basteria.ply")

            while running :
                dt =clock .tick (60 )/1000.0
                running =self .handle_events ()
                self .update (dt )
                self .render ()

            self .cap .release ()
            cv2 .destroyAllWindows ()
            pygame .quit ()
            sys .exit ()
        except Exception as e :
            print (f' Error en el bucle principal: {e}')
            import traceback
            traceback .print_exc ()
            self .cap .release ()
            cv2 .destroyAllWindows ()
            pygame .quit ()
            sys .exit (1 )

if __name__ =="__main__":
    try :
        simulation =PCRCameraSimulation ()
        simulation .run ()
    except Exception as e :
        print (f' Error en la inicialización de la simulación: {e}')
        import traceback
        traceback .print_exc ()
        sys .exit (1 )
