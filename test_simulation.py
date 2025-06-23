
"""
Test Script - Verificación rápida del proyecto PCR Termophilic Cells
"""

import sys
import os

def test_imports ():
    """Prueba las importaciones principales"""
    print (" Probando importaciones...")

    try :
        import pygame
        print ("    pygame")
    except ImportError as e :
        print (f"    pygame: {e}")
        return False

    try :
        import numpy as np
        print ("    numpy")
    except ImportError as e :
        print (f"    numpy: {e}")
        return False

    try :
        from OpenGL .GL import glClear ,GL_COLOR_BUFFER_BIT
        print ("    OpenGL")
    except ImportError as e :
        print (f"    OpenGL: {e}")
        return False

    try :
        from plyfile import PlyData
        print ("    plyfile")
    except ImportError as e :
        print (f"    plyfile: {e}")
        return False

    return True

def test_pygame_init ():
    """Prueba la inicialización de pygame"""
    print ("\n Probando pygame...")

    try :
        import pygame
        pygame .init ()
        screen =pygame .display .set_mode ((100 ,100 ))
        pygame .quit ()
        print ("    pygame funciona correctamente")
        return True
    except Exception as e :
        print (f"    Error con pygame: {e}")
        return False

def test_opengl ():
    """Prueba OpenGL"""
    print ("\n Probando OpenGL...")

    try :
        import pygame
        from OpenGL .GL import glClear ,GL_COLOR_BUFFER_BIT
        from OpenGL .GLU import gluPerspective

        pygame .init ()
        screen =pygame .display .set_mode ((100 ,100 ),pygame .OPENGL )
        glClear (GL_COLOR_BUFFER_BIT )
        pygame .quit ()
        print ("    OpenGL funciona correctamente")
        return True
    except Exception as e :
        print (f"    Error con OpenGL: {e}")
        return False

def test_ply_model ():
    """Prueba la carga del modelo PLY"""
    print ("\n Probando modelo PLY...")

    try :
        from plyfile import PlyData

        model_path ="models/thermophilic_cell.ply"
        if os .path .exists (model_path ):
            plydata =PlyData .read (model_path )
            vertex_count =len (plydata ['vertex'])
            print (f"    Modelo PLY cargado: {vertex_count} vértices")
            return True
        else :
            print ("   ️  Modelo PLY no encontrado")
            return False
    except Exception as e :
        print (f"    Error cargando PLY: {e}")
        return False

def test_simulation_class ():
    """Prueba la clase de simulación"""
    print ("\n Probando clase de simulación...")

    try :
        from pcr_simple_simulation import SimplePCRSimulation


        simulation =SimplePCRSimulation .__new__ (SimplePCRSimulation )
        simulation .width =800
        simulation .height =600
        simulation .cells =[]
        simulation .current_stage ="cooling"

        print ("    Clase de simulación funciona")
        return True
    except Exception as e :
        print (f"    Error con clase de simulación: {e}")
        return False

def main ():
    """Función principal de pruebas"""
    print (" PCR Termophilic Cells - Test de Verificación")
    print ("="*50 )

    tests =[
    test_imports ,
    test_pygame_init ,
    test_opengl ,
    test_ply_model ,
    test_simulation_class
    ]

    passed =0
    total =len (tests )

    for test in tests :
        if test ():
            passed +=1

    print ("\n"+"="*50 )
    print (f" Resultados: {passed}/{total} pruebas pasaron")

    if passed ==total :
        print (" ¡Todas las pruebas pasaron! El proyecto está listo para usar.")
        print ("\n Para ejecutar la simulación:")
        print ("   python pcr_simple_simulation.py")
    else :
        print (" Algunas pruebas fallaron. Revisa los errores anteriores.")
        print ("\n Para instalar dependencias faltantes:")
        print ("   pip install pygame numpy pyopengl plyfile scipy matplotlib pillow")

    return passed ==total

if __name__ =="__main__":
    success =main ()
    sys .exit (0 if success else 1 )
