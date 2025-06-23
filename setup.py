
"""
Setup script para PCR Termophilic Cells Interactive Videomapping
Instala dependencias y configura el entorno
"""

import subprocess
import sys
import os
import platform

def check_python_version ():
    """Verifica que la versión de Python sea compatible"""
    if sys .version_info <(3 ,8 ):
        print (" Error: Se requiere Python 3.8 o superior")
        print (f"   Versión actual: {sys.version}")
        return False
    print (f" Python {sys.version.split()[0]} detectado")
    return True

def install_dependencies ():
    """Instala las dependencias del proyecto"""
    print ("\n Instalando dependencias...")

    dependencies =[
    "opencv-python>=4.8.0",
    "mediapipe>=0.10.0",
    "pygame>=2.5.0",
    "numpy>=1.24.0",
    "pyopengl>=3.1.6",
    "plyfile>=0.7.4",
    "scipy>=1.10.0",
    "matplotlib>=3.7.0",
    "pillow>=9.5.0"
    ]

    for dep in dependencies :
        print (f"   Instalando {dep}...")
        try :
            subprocess .check_call ([sys .executable ,"-m","pip","install",dep ])
            print (f"    {dep} instalado correctamente")
        except subprocess .CalledProcessError :
            print (f"    Error instalando {dep}")
            return False

    return True

def check_camera ():
    """Verifica que la cámara esté disponible"""
    print ("\n Verificando cámara...")
    try :
        import cv2
        cap =cv2 .VideoCapture (0 )
        if cap .isOpened ():
            ret ,frame =cap .read ()
            cap .release ()
            if ret :
                print (" Cámara detectada y funcionando")
                return True
            else :
                print ("️  Cámara detectada pero no puede capturar imágenes")
                return False
        else :
            print (" No se pudo acceder a la cámara")
            return False
    except Exception as e :
        print (f" Error verificando cámara: {e}")
        return False

def check_opengl ():
    """Verifica que OpenGL esté disponible"""
    print ("\n Verificando OpenGL...")
    try :
        import pygame
        pygame .init ()
        pygame .display .set_mode ((100 ,100 ),pygame .OPENGL )
        pygame .quit ()
        print (" OpenGL disponible")
        return True
    except Exception as e :
        print (f" Error con OpenGL: {e}")
        return False

def create_directories ():
    """Crea directorios necesarios"""
    print ("\n Creando directorios...")

    directories =["models","data","logs"]
    for directory in directories :
        if not os .path .exists (directory ):
            os .makedirs (directory )
            print (f"    Creado directorio: {directory}")
        else :
            print (f"    Directorio ya existe: {directory}")

def create_config_file ():
    """Crea archivo de configuración por defecto"""
    print ("\n️  Creando archivo de configuración...")

    config_content ="""# Configuración para PCR Termophilic Cells Interactive
# Archivo de configuración

[Display]
width = 1280
height = 720
fullscreen = false
vsync = true

[Camera]
device = 0
width = 640
height = 480
fps = 30

[PCR]
auto_advance = true
cycle_duration = 3.0
max_cycles = 30

[Cells]
initial_count = 50
max_divisions = 3
energy_consumption = 5.0

[Effects]
show_particles = true
show_dna = true
show_camera = true
particle_count = 100

[Controls]
mouse_sensitivity = 0.01
hand_influence_radius = 2.0
"""

    try :
        with open ("config.ini","w")as f :
            f .write (config_content )
        print ("    Archivo config.ini creado")
    except Exception as e :
        print (f"    Error creando config.ini: {e}")

def run_test ():
    """Ejecuta una prueba básica del sistema"""
    print ("\n Ejecutando prueba del sistema...")

    try :

        import pygame
        import cv2
        import mediapipe as mp
        import numpy as np
        from OpenGL .GL import glClear ,GL_COLOR_BUFFER_BIT
        from plyfile import PlyData

        print ("    Todos los módulos importados correctamente")


        pygame .init ()
        screen =pygame .display .set_mode ((100 ,100 ))
        pygame .quit ()
        print ("    Pygame funcionando")


        cap =cv2 .VideoCapture (0 )
        if cap .isOpened ():
            cap .release ()
            print ("    OpenCV funcionando")

        print (" Prueba del sistema completada exitosamente")
        return True

    except Exception as e :
        print (f"    Error en prueba del sistema: {e}")
        return False

def show_usage ():
    """Muestra información de uso"""
    print ("\n"+"="*60 )
    print (" ¡Instalación completada!")
    print ("="*60 )
    print ("\n Para ejecutar el proyecto:")
    print ("   python pcr_thermophilic_simulation.py")
    print ("   python pcr_advanced_simulation.py")
    print ("\n Controles principales:")
    print ("   ESPACIO - Siguiente etapa PCR")
    print ("   R - Reiniciar simulación")
    print ("   P - Pausar/Reanudar")
    print ("   C - Mostrar/Ocultar cámara")
    print ("   ESC - Salir")
    print ("\n Documentación:")
    print ("   README.md - Guía completa del proyecto")
    print ("\n Configuración:")
    print ("   config.ini - Ajustes del sistema")
    print ("\n"+"="*60 )

def main ():
    """Función principal del setup"""
    print (" PCR Termophilic Cells Interactive Videomapping")
    print ("="*60 )


    if not check_python_version ():
        return False


    if not install_dependencies ():
        print (" Error instalando dependencias")
        return False


    create_directories ()


    create_config_file ()


    camera_ok =check_camera ()
    opengl_ok =check_opengl ()

    if not camera_ok :
        print ("️  Advertencia: La cámara no está disponible")
        print ("   El proyecto funcionará pero sin interactividad de manos")

    if not opengl_ok :
        print (" Error: OpenGL no está disponible")
        print ("   El proyecto requiere OpenGL para funcionar")
        return False


    if run_test ():
        show_usage ()
        return True
    else :
        print (" Error en la prueba del sistema")
        return False

if __name__ =="__main__":
    success =main ()
    if not success :
        print ("\n La instalación no se completó correctamente")
        print ("   Revisa los errores anteriores e intenta nuevamente")
        sys .exit (1 )
    else :
        print ("\n Instalación completada exitosamente")
        sys .exit (0 )
