
"""
PLY Cell Renderer - Renderizador especializado para células termófilas
Maneja la carga y renderizado de modelos PLY con efectos visuales avanzados
"""

import numpy as np
from OpenGL .GL import *
from OpenGL .GLU import *
from plyfile import PlyData
import math
import random
from typing import List ,Tuple ,Optional ,Dict ,Any

class PLYCellModel :
    """Modelo 3D de célula cargado desde archivo PLY"""

    def __init__ (self ,filename :str ):
        self .vertices =[]
        self .normals =[]
        self .colors =[]
        self .indices =[]
        self .center =np .array ([0.0 ,0.0 ,0.0 ])
        self .bounding_box =None
        self .load_ply (filename )

    def load_ply (self ,filename :str ):
        """Carga un archivo PLY y extrae la geometría"""
        try :
            plydata =PlyData .read (filename )
            vertex_data =plydata ['vertex']


            if 'x'in vertex_data .dtype .names and 'y'in vertex_data .dtype .names and 'z'in vertex_data .dtype .names :
                self .vertices =np .column_stack ([
                vertex_data ['x'],
                vertex_data ['y'],
                vertex_data ['z']
                ])


            if 'nx'in vertex_data .dtype .names and 'ny'in vertex_data .dtype .names and 'nz'in vertex_data .dtype .names :
                self .normals =np .column_stack ([
                vertex_data ['nx'],
                vertex_data ['ny'],
                vertex_data ['nz']
                ])


            if 'red'in vertex_data .dtype .names and 'green'in vertex_data .dtype .names and 'blue'in vertex_data .dtype .names :
                self .colors =np .column_stack ([
                vertex_data ['red']/255.0 ,
                vertex_data ['green']/255.0 ,
                vertex_data ['blue']/255.0
                ])
            else :

                self .colors =np .full ((len (self .vertices ),3 ),[0.2 ,0.8 ,0.2 ])


            if 'face'in plydata :
                face_data =plydata ['face']
                if 'vertex_indices'in face_data .dtype .names :
                    self .indices =np .array ([face ['vertex_indices']for face in face_data ])


            if len (self .vertices )>0 :
                self .center =np .mean (self .vertices ,axis =0 )
                min_coords =np .min (self .vertices ,axis =0 )
                max_coords =np .max (self .vertices ,axis =0 )
                self .bounding_box =(min_coords ,max_coords )


                self .vertices -=self .center

            print (f"PLY cargado: {len(self.vertices)} vértices, {len(self.indices)} caras")

        except Exception as e :
            print (f"Error cargando PLY {filename}: {e}")

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
        self .bounding_box =(np .array ([-radius ,-radius ,-radius ]),np .array ([radius ,radius ,radius ]))

class ThermophilicCellRenderer :
    """Renderizador especializado para células termófilas"""

    def __init__ (self ):
        self .cell_models :Dict [str ,PLYCellModel ]={}
        self .particle_systems =[]
        self .dna_strands =[]


        self .glow_intensity =0.0
        self .heat_distortion =0.0
        self .energy_particles =[]

    def load_cell_model (self ,name :str ,filename :str ):
        """Carga un modelo de célula desde archivo PLY"""
        self .cell_models [name ]=PLYCellModel (filename )

    def create_energy_particle (self ,position :np .ndarray ,velocity :np .ndarray ,
    color :Tuple [float ,float ,float ],lifetime :float ):
        """Crea una partícula de energía"""
        return {
        'position':position .copy (),
        'velocity':velocity .copy (),
        'color':color ,
        'lifetime':lifetime ,
        'max_lifetime':lifetime ,
        'size':random .uniform (0.1 ,0.3 )
        }

    def update_energy_particles (self ,dt :float ):
        """Actualiza las partículas de energía"""
        for particle in self .energy_particles [:]:
            particle ['lifetime']-=dt
            particle ['position']+=particle ['velocity']*dt
            particle ['velocity']*=0.98


            particle ['velocity'][1 ]-=2.0 *dt

            if particle ['lifetime']<=0 :
                self .energy_particles .remove (particle )

    def render_cell_model (self ,model :PLYCellModel ,position :np .ndarray ,
    scale :float =1.0 ,rotation :np .ndarray =None ,
    color :Optional [Tuple [float ,float ,float ]]=None ,
    temperature :float =25.0 ):
        """Renderiza un modelo de célula con efectos de temperatura"""

        glPushMatrix ()
        glTranslatef (position [0 ],position [1 ],position [2 ])
        glScalef (scale ,scale ,scale )

        if rotation is not None :
            glRotatef (rotation [0 ],1 ,0 ,0 )
            glRotatef (rotation [1 ],0 ,1 ,0 )
            glRotatef (rotation [2 ],0 ,0 ,1 )


        if temperature >80 :

            glEnable (GL_BLEND )
            glBlendFunc (GL_SRC_ALPHA ,GL_ONE )


            intensity =(temperature -80 )/20.0
            glColor4f (1.0 ,0.3 ,0.1 ,intensity *0.5 )
            glScalef (1.1 ,1.1 ,1.1 )
            self .render_geometry (model )

            glScalef (0.9 ,0.9 ,0.9 )
            glBlendFunc (GL_SRC_ALPHA ,GL_ONE_MINUS_SRC_ALPHA )


        if color :
            base_color =color
        else :

            if temperature >80 :
                base_color =(0.8 ,0.2 ,0.2 )
            elif temperature >60 :
                base_color =(0.8 ,0.6 ,0.2 )
            elif temperature >40 :
                base_color =(0.8 ,0.8 ,0.2 )
            else :
                base_color =(0.2 ,0.8 ,0.2 )

        glColor3f (*base_color )
        self .render_geometry (model )


        if temperature >50 :

            if random .random ()<0.1 :
                particle_pos =position +np .random .uniform (-0.5 ,0.5 ,3 )
                particle_vel =np .random .uniform (-1 ,1 ,3 )
                particle_vel [1 ]=abs (particle_vel [1 ])

                self .energy_particles .append (
                self .create_energy_particle (
                particle_pos ,particle_vel ,
                (1.0 ,1.0 ,0.5 ),2.0
                )
                )

        glPopMatrix ()

    def render_geometry (self ,model :PLYCellModel ):
        """Renderiza la geometría del modelo"""
        if len (model .indices )>0 :

            glEnableClientState (GL_VERTEX_ARRAY )
            glEnableClientState (GL_NORMAL_ARRAY )
            glEnableClientState (GL_COLOR_ARRAY )

            glVertexPointer (3 ,GL_FLOAT ,0 ,model .vertices )
            if len (model .normals )>0 :
                glNormalPointer (GL_FLOAT ,0 ,model .normals )
            glColorPointer (3 ,GL_FLOAT ,0 ,model .colors )

            glDrawElements (GL_TRIANGLES ,len (model .indices )*3 ,GL_UNSIGNED_INT ,model .indices )

            glDisableClientState (GL_VERTEX_ARRAY )
            glDisableClientState (GL_NORMAL_ARRAY )
            glDisableClientState (GL_COLOR_ARRAY )
        else :

            glEnableClientState (GL_VERTEX_ARRAY )
            glEnableClientState (GL_COLOR_ARRAY )

            glVertexPointer (3 ,GL_FLOAT ,0 ,model .vertices )
            glColorPointer (3 ,GL_FLOAT ,0 ,model .colors )

            glPointSize (3.0 )
            glDrawArrays (GL_POINTS ,0 ,len (model .vertices ))

            glDisableClientState (GL_VERTEX_ARRAY )
            glDisableClientState (GL_COLOR_ARRAY )

    def render_energy_particles (self ):
        """Renderiza las partículas de energía"""
        glEnable (GL_BLEND )
        glBlendFunc (GL_SRC_ALPHA ,GL_ONE )
        glEnable (GL_POINT_SMOOTH )

        for particle in self .energy_particles :
            alpha =particle ['lifetime']/particle ['max_lifetime']
            glColor4f (*particle ['color'],alpha )
            glPointSize (particle ['size']*10 )

            glBegin (GL_POINTS )
            glVertex3f (*particle ['position'])
            glEnd ()

        glDisable (GL_POINT_SMOOTH )
        glBlendFunc (GL_SRC_ALPHA ,GL_ONE_MINUS_SRC_ALPHA )
        glDisable (GL_BLEND )

    def render_dna_strands (self ,pcr_stage :str ):
        """Renderiza hebras de DNA durante el proceso de PCR"""
        if pcr_stage =="denaturation":

            self .render_separating_dna ()
        elif pcr_stage =="annealing":

            self .render_annealing_dna ()
        elif pcr_stage =="extension":

            self .render_extending_dna ()

    def render_separating_dna (self ):
        """Renderiza DNA separándose durante desnaturalización"""
        glColor3f (0.8 ,0.8 ,1.0 )
        glLineWidth (2.0 )

        for i in range (5 ):
            y_offset =i *0.5 -1.0
            separation =math .sin (pygame .time .get_ticks ()*0.001 +i )*0.3

            glBegin (GL_LINES )

            glVertex3f (-2.0 +separation ,y_offset ,0 )
            glVertex3f (2.0 +separation ,y_offset ,0 )

            glVertex3f (-2.0 -separation ,y_offset +0.1 ,0 )
            glVertex3f (2.0 -separation ,y_offset +0.1 ,0 )
            glEnd ()

    def render_annealing_dna (self ):
        """Renderiza primers uniéndose al DNA"""
        glColor3f (1.0 ,0.5 ,0.0 )
        glLineWidth (3.0 )

        for i in range (3 ):
            y_offset =i *0.8 -1.0
            primer_pos =math .sin (pygame .time .get_ticks ()*0.002 +i )*0.5

            glBegin (GL_LINES )

            glVertex3f (-1.5 +primer_pos ,y_offset ,0 )
            glVertex3f (-0.5 +primer_pos ,y_offset ,0 )
            glEnd ()

    def render_extending_dna (self ):
        """Renderiza síntesis de nueva cadena"""
        glColor3f (0.2 ,1.0 ,0.2 )
        glLineWidth (2.0 )

        extension =(pygame .time .get_ticks ()*0.001 )%4.0

        glBegin (GL_LINES )
        glVertex3f (-2.0 ,0 ,0 )
        glVertex3f (-2.0 +extension ,0 ,0 )
        glEnd ()

    def update (self ,dt :float ):
        """Actualiza el renderizador"""
        self .update_energy_particles (dt )


        self .glow_intensity =math .sin (pygame .time .get_ticks ()*0.003 )*0.5 +0.5
        self .heat_distortion =math .sin (pygame .time .get_ticks ()*0.005 )*0.1

class CellFactory :
    """Fábrica para crear diferentes tipos de células termófilas"""

    @staticmethod
    def create_thermus_aquaticus (position :np .ndarray )->Dict [str ,Any ]:
        """Crea una célula de Thermus aquaticus (descubierta en Yellowstone)"""
        return {
        'type':'thermus_aquaticus',
        'position':position ,
        'optimal_temp':70.0 ,
        'max_temp':80.0 ,
        'color':(0.8 ,0.6 ,0.2 ),
        'size':1.2 ,
        'energy_efficiency':0.9
        }

    @staticmethod
    def create_pyrococcus_furiosus (position :np .ndarray )->Dict [str ,Any ]:
        """Crea una célula de Pyrococcus furiosus (extremófila)"""
        return {
        'type':'pyrococcus_furiosus',
        'position':position ,
        'optimal_temp':100.0 ,
        'max_temp':105.0 ,
        'color':(0.8 ,0.2 ,0.2 ),
        'size':1.0 ,
        'energy_efficiency':0.95
        }

    @staticmethod
    def create_thermococcus_litoralis (position :np .ndarray )->Dict [str ,Any ]:
        """Crea una célula de Thermococcus litoralis (marina)"""
        return {
        'type':'thermococcus_litoralis',
        'position':position ,
        'optimal_temp':88.0 ,
        'max_temp':98.0 ,
        'color':(0.6 ,0.8 ,0.2 ),
        'size':0.8 ,
        'energy_efficiency':0.85
        }
