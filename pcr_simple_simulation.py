
"""
PCR Simple Simulation - Versión simplificada sin MediaPipe
Simulación del proceso de PCR usando células termófilas (compatible con Python 3.13)
"""

import pygame
import numpy as np
import sys
import os
import math
import random
from typing import List ,Tuple ,Optional
from OpenGL .GL import *
from OpenGL .GLU import *

class PCRStage :
    """Estados del proceso de PCR"""
    DENATURATION ="denaturation"
    ANNEALING ="annealing"
    EXTENSION ="extension"
    COOLING ="cooling"

class SimpleThermophilicCell :
    """Representación simplificada de una célula termófila"""

    def __init__ (self ,x :float ,y :float ,z :float ):
        self .x =x
        self .y =y
        self .z =z
        self .original_x =x
        self .original_y =y
        self .original_z =z
        self .temperature =25.0
        self .target_temp =25.0
        self .energy =100.0
        self .active =True
        self .color =(0.2 ,0.8 ,0.2 )
        self .size =random .uniform (0.5 ,1.5 )
        self .animation_phase =random .uniform (0 ,2 *math .pi )

    def update (self ,dt :float ,pcr_stage :str ,mouse_pos :Optional [Tuple [float ,float ,float ]]=None ):
        """Actualiza el estado de la célula"""


        if pcr_stage ==PCRStage .DENATURATION :
            self .target_temp =94.0
        elif pcr_stage ==PCRStage .ANNEALING :
            self .target_temp =55.0
        elif pcr_stage ==PCRStage .EXTENSION :
            self .target_temp =72.0
        else :
            self .target_temp =25.0


        if mouse_pos :
            mouse_x ,mouse_y ,mouse_z =mouse_pos
            distance =math .sqrt ((self .x -mouse_x )**2 +(self .y -mouse_y )**2 +(self .z -mouse_z )**2 )

            if distance <3.0 :

                self .energy =min (100.0 ,self .energy +10.0 *dt )
                self .active =True


                influence =max (0 ,1.0 -distance /3.0 )
                self .x +=(mouse_x -self .x )*influence *dt *0.5
                self .y +=(mouse_y -self .y )*influence *dt *0.5
                self .z +=(mouse_z -self .z )*influence *dt *0.5


        temp_diff =self .target_temp -self .temperature
        self .temperature +=temp_diff *dt *2.0


        if self .temperature >80 :
            self .color =(0.8 ,0.2 ,0.2 )
        elif self .temperature >60 :
            self .color =(0.8 ,0.6 ,0.2 )
        elif self .temperature >40 :
            self .color =(0.8 ,0.8 ,0.2 )
        else :
            self .color =(0.2 ,0.8 ,0.2 )


        if self .active :
            self .energy -=dt *5.0
            if self .energy <=0 :
                self .active =False
                self .color =(0.5 ,0.5 ,0.5 )


        self .animation_phase +=dt *2.0
        self .y +=math .sin (self .animation_phase )*dt *0.1

class SimplePCRSimulation :
    """Simulación simplificada del proceso de PCR"""

    def __init__ (self ,width :int =1280 ,height :int =720 ):
        pygame .init ()
        self .width =width
        self .height =height
        self .screen =pygame .display .set_mode ((width ,height ),pygame .OPENGL |pygame .DOUBLEBUF )
        pygame .display .set_caption ("PCR Simple - Termophilic Cells")


        glEnable (GL_DEPTH_TEST )
        glEnable (GL_BLEND )
        glBlendFunc (GL_SRC_ALPHA ,GL_ONE_MINUS_SRC_ALPHA )
        glClearColor (0.0 ,0.0 ,0.1 ,1.0 )


        self .camera_distance =10.0
        self .camera_rotation_x =0.0
        self .camera_rotation_y =0.0


        self .current_stage =PCRStage .COOLING
        self .stage_timer =0.0
        self .cycle_count =0
        self .max_cycles =30


        self .cells :List [SimpleThermophilicCell ]=[]
        self .generate_cells (50 )


        self .mouse_pos =None
        self .mouse_pressed =False


        self .paused =False

    def generate_cells (self ,count :int ):
        """Genera células termófilas aleatorias"""
        for _ in range (count ):
            x =random .uniform (-8 ,8 )
            y =random .uniform (-4 ,4 )
            z =random .uniform (-5 ,5 )
            self .cells .append (SimpleThermophilicCell (x ,y ,z ))

    def handle_events (self ):
        """Maneja eventos de pygame"""
        for event in pygame .event .get ():
            if event .type ==pygame .QUIT :
                return False
            elif event .type ==pygame .KEYDOWN :
                if event .key ==pygame .K_ESCAPE :
                    return False
                elif event .key ==pygame .K_SPACE :
                    self .next_pcr_stage ()
                elif event .key ==pygame .K_p :
                    self .paused =not self .paused
                elif event .key ==pygame .K_r :
                    self .reset_simulation ()
            elif event .type ==pygame .MOUSEMOTION :
                if event .buttons [0 ]:
                    self .camera_rotation_y +=event .rel [0 ]*0.01
                    self .camera_rotation_x +=event .rel [1 ]*0.01


                    mouse_x ,mouse_y =event .pos
                    normalized_x =(mouse_x /self .width -0.5 )*16
                    normalized_y =(0.5 -mouse_y /self .height )*8
                    self .mouse_pos =(normalized_x ,normalized_y ,0 )
                else :
                    self .mouse_pos =None
            elif event .type ==pygame .MOUSEBUTTONDOWN :
                if event .button ==1 :
                    self .mouse_pressed =True
                elif event .button ==4 :
                    self .camera_distance =max (2.0 ,self .camera_distance -0.5 )
                elif event .button ==5 :
                    self .camera_distance =min (20.0 ,self .camera_distance +0.5 )
            elif event .type ==pygame .MOUSEBUTTONUP :
                if event .button ==1 :
                    self .mouse_pressed =False
                    self .mouse_pos =None

        return True

    def next_pcr_stage (self ):
        """Avanza a la siguiente etapa del PCR"""
        if self .current_stage ==PCRStage .COOLING :
            self .current_stage =PCRStage .DENATURATION
            self .stage_timer =0.0
        elif self .current_stage ==PCRStage .DENATURATION :
            self .current_stage =PCRStage .ANNEALING
            self .stage_timer =0.0
        elif self .current_stage ==PCRStage .ANNEALING :
            self .current_stage =PCRStage .EXTENSION
            self .stage_timer =0.0
        elif self .current_stage ==PCRStage .EXTENSION :
            self .current_stage =PCRStage .COOLING
            self .stage_timer =0.0
            self .cycle_count +=1

    def reset_simulation (self ):
        """Reinicia la simulación"""
        self .current_stage =PCRStage .COOLING
        self .stage_timer =0.0
        self .cycle_count =0
        for cell in self .cells :
            cell .temperature =25.0
            cell .energy =100.0
            cell .active =True
            cell .x =cell .original_x
            cell .y =cell .original_y
            cell .z =cell .original_z

    def update (self ,dt :float ):
        """Actualiza la simulación"""
        if self .paused :
            return


        self .stage_timer +=dt


        stage_duration =3.0
        if self .stage_timer >=stage_duration :
            self .next_pcr_stage ()


        for cell in self .cells :
            cell .update (dt ,self .current_stage ,self .mouse_pos )

    def render_cells (self ):
        """Renderiza las células termófilas"""
        glEnable (GL_POINT_SMOOTH )
        glPointSize (8.0 )

        glBegin (GL_POINTS )
        for cell in self .cells :
            if cell .active :
                glColor3f (*cell .color )
                glVertex3f (cell .x ,cell .y ,cell .z )
        glEnd ()


        glColor3f (0.5 ,0.5 ,0.5 )
        glBegin (GL_POINTS )
        for cell in self .cells :
            if not cell .active :
                glVertex3f (cell .x ,cell .y ,cell .z )
        glEnd ()

    def render_dna_visualization (self ):
        """Renderiza visualización simplificada del DNA"""
        glColor3f (0.8 ,0.8 ,1.0 )
        glLineWidth (2.0 )


        glBegin (GL_LINES )
        for i in range (3 ):
            y_offset =i *0.5 -1.0
            if self .current_stage ==PCRStage .DENATURATION :

                separation =math .sin (pygame .time .get_ticks ()*0.001 +i )*0.3
                glVertex3f (-2.0 +separation ,y_offset ,0 )
                glVertex3f (2.0 +separation ,y_offset ,0 )
                glVertex3f (-2.0 -separation ,y_offset +0.1 ,0 )
                glVertex3f (2.0 -separation ,y_offset +0.1 ,0 )
            else :

                glVertex3f (-2.0 ,y_offset ,0 )
                glVertex3f (2.0 ,y_offset ,0 )
        glEnd ()

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


        stage_text =f"Etapa: {self.current_stage.upper()}"
        stage_surface =font .render (stage_text ,True ,(255 ,255 ,255 ))
        self .screen .blit (stage_surface ,(10 ,self .height -100 ))


        cycle_text =f"Ciclo: {self.cycle_count}/{self.max_cycles}"
        cycle_surface =font .render (cycle_text ,True ,(255 ,255 ,255 ))
        self .screen .blit (cycle_surface ,(10 ,self .height -70 ))


        avg_temp =sum (cell .temperature for cell in self .cells )/len (self .cells )
        temp_text =f"Temperatura: {avg_temp:.1f}°C"
        temp_surface =font .render (temp_text ,True ,(255 ,255 ,255 ))
        self .screen .blit (temp_surface ,(10 ,self .height -40 ))


        controls_font =pygame .font .Font (None ,24 )
        controls =[
        "ESPACIO: Siguiente etapa",
        "R: Reiniciar",
        "P: Pausar/Reanudar",
        "Mouse: Rotar cámara e interactuar",
        "Scroll: Zoom"
        ]

        for i ,control in enumerate (controls ):
            control_surface =controls_font .render (control ,True ,(200 ,200 ,200 ))
            self .screen .blit (control_surface ,(self .width -300 ,10 +i *25 ))


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


        self .render_dna_visualization ()


        self .render_ui ()

        pygame .display .flip ()

    def run (self ):
        """Bucle principal de la aplicación"""
        clock =pygame .time .Clock ()
        running =True

        print (" PCR Simple Simulation iniciado")
        print (" Controles:")
        print ("   - ESPACIO: Siguiente etapa PCR")
        print ("   - R: Reiniciar simulación")
        print ("   - P: Pausar/Reanudar")
        print ("   - Mouse: Rotar cámara e interactuar con células")
        print ("   - Scroll: Zoom")
        print ("   - ESC: Salir")

        while running :
            dt =clock .tick (60 )/1000.0

            running =self .handle_events ()
            self .update (dt )
            self .render ()

        pygame .quit ()
        sys .exit ()

if __name__ =="__main__":
    simulation =SimplePCRSimulation ()
    simulation .run ()
