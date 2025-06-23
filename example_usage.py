
"""
Ejemplo de uso para PCR Termophilic Cells Interactive Videomapping
Demuestra diferentes configuraciones y características del proyecto
"""

import sys
import os
import time

def print_banner ():
    """Imprime el banner del proyecto"""
    print ("="*70 )
    print (" PCR Termophilic Cells Interactive Videomapping")
    print ("   Ejemplo de uso y configuración")
    print ("="*70 )

def check_requirements ():
    """Verifica que los requisitos estén instalados"""
    print (" Verificando requisitos...")

    required_modules =[
    "pygame","cv2","mediapipe","numpy",
    "OpenGL","plyfile","scipy","matplotlib"
    ]

    missing_modules =[]

    for module in required_modules :
        try :
            if module =="cv2":
                import cv2
            elif module =="OpenGL":
                from OpenGL .GL import glClear
            else :
                __import__ (module )
            print (f"    {module}")
        except ImportError :
            print (f"    {module} - No encontrado")
            missing_modules .append (module )

    if missing_modules :
        print (f"\n Faltan módulos: {', '.join(missing_modules)}")
        print ("   Ejecuta: python setup.py")
        return False

    print (" Todos los requisitos están instalados")
    return True

def run_basic_simulation ():
    """Ejecuta la simulación básica"""
    print ("\n Ejecutando simulación básica...")
    print ("   Presiona ESC para salir")

    try :
        from pcr_thermophilic_simulation import PCRSimulation
        simulation =PCRSimulation ()
        simulation .run ()
    except Exception as e :
        print (f"    Error: {e}")

def run_advanced_simulation ():
    """Ejecuta la simulación avanzada"""
    print ("\n Ejecutando simulación avanzada...")
    print ("   Presiona ESC para salir")

    try :
        from pcr_advanced_simulation import AdvancedPCRSimulation
        simulation =AdvancedPCRSimulation ()
        simulation .run ()
    except Exception as e :
        print (f"    Error: {e}")

def demonstrate_ply_loading ():
    """Demuestra la carga de modelos PLY"""
    print ("\n Demostrando carga de modelos PLY...")

    try :
        from ply_cell_renderer import PLYCellModel


        model_path ="models/thermophilic_cell.ply"
        if os .path .exists (model_path ):
            model =PLYCellModel (model_path )
            print (f"    Modelo cargado: {len(model.vertices)} vértices")
            print (f"    Caras: {len(model.indices)}")
        else :
            print (f"   ️  Modelo no encontrado: {model_path}")
            print ("   Creando modelo por defecto...")
            model =PLYCellModel ("nonexistent.ply")
            print (f"    Modelo por defecto creado: {len(model.vertices)} vértices")

    except Exception as e :
        print (f"    Error: {e}")

def demonstrate_cell_factory ():
    """Demuestra la fábrica de células"""
    print ("\n Demostrando fábrica de células...")

    try :
        from ply_cell_renderer import CellFactory
        import numpy as np


        position =np .array ([0.0 ,0.0 ,0.0 ])

        cell_types =[
        ("Thermus aquaticus",CellFactory .create_thermus_aquaticus ),
        ("Pyrococcus furiosus",CellFactory .create_pyrococcus_furiosus ),
        ("Thermococcus litoralis",CellFactory .create_thermococcus_litoralis )
        ]

        for name ,factory_func in cell_types :
            cell_data =factory_func (position )
            print (f"    {name}:")
            print (f"      Temperatura óptima: {cell_data['optimal_temp']}°C")
            print (f"      Temperatura máxima: {cell_data['max_temp']}°C")
            print (f"      Color: {cell_data['color']}")
            print (f"      Tamaño: {cell_data['size']}")

    except Exception as e :
        print (f"    Error: {e}")

def show_interaction_guide ():
    """Muestra la guía de interacción"""
    print ("\n Guía de Interacción:")
    print ("    Mueve tus manos frente a la cámara")
    print ("    Las células reaccionarán a tu presencia")
    print ("    Toca las células para activarlas")
    print ("   ️  Observa cómo cambian de color con la temperatura")
    print ("    Las células liberan partículas de energía")
    print ("    El proceso de PCR avanza automáticamente")

def show_controls ():
    """Muestra los controles disponibles"""
    print ("\n Controles del Teclado:")
    print ("   ESPACIO - Avanzar manualmente a la siguiente etapa")
    print ("   R       - Reiniciar la simulación")
    print ("   P       - Pausar/Reanudar")
    print ("   C       - Mostrar/Ocultar vista de cámara")
    print ("   A       - Activar/Desactivar auto-avance")
    print ("   D       - Mostrar/Ocultar visualización de DNA")
    print ("   T       - Mostrar/Ocultar partículas")
    print ("   ESC     - Salir")

def show_pcr_stages ():
    """Muestra información sobre las etapas del PCR"""
    print ("\n Etapas del PCR Simuladas:")
    print ("   1.  Desnaturalización (94°C)")
    print ("      - Separación de cadenas de DNA")
    print ("      - Células cambian a rojo intenso")
    print ("      - Efectos de calor extremo")
    print ()
    print ("   2.  Annealing (50-65°C)")
    print ("      - Unión de primers al DNA")
    print ("      - Células en color naranja")
    print ("      - Visualización de primers")
    print ()
    print ("   3.  Extensión (72°C)")
    print ("      - Síntesis de nueva cadena de DNA")
    print ("      - Células en color amarillo")
    print ("      - Efectos de síntesis")
    print ()
    print ("   4. ️  Enfriamiento (25°C)")
    print ("      - Preparación para el siguiente ciclo")
    print ("      - Células regresan a color verde")
    print ("      - Recuperación de energía")

def main ():
    """Función principal"""
    print_banner ()


    if not check_requirements ():
        return


    show_pcr_stages ()
    show_interaction_guide ()
    show_controls ()


    demonstrate_ply_loading ()
    demonstrate_cell_factory ()


    while True :
        print ("\n"+"="*50 )
        print (" ¿Qué quieres hacer?")
        print ("   1. Ejecutar simulación básica")
        print ("   2. Ejecutar simulación avanzada")
        print ("   3. Ver información del proyecto")
        print ("   4. Salir")

        try :
            choice =input ("\n   Selecciona una opción (1-4): ").strip ()

            if choice =="1":
                run_basic_simulation ()
            elif choice =="2":
                run_advanced_simulation ()
            elif choice =="3":
                print ("\n Información del Proyecto:")
                print ("    Simula el proceso de PCR usando células termófilas")
                print ("    Interactividad con detección de manos (MediaPipe)")
                print ("    Visualización 3D con OpenGL y modelos PLY")
                print ("    Células termófilas reales: Thermus aquaticus, etc.")
                print ("    Educativo: Historia del PCR y biología molecular")
                print ("    Artístico: Videomapping interactivo")
            elif choice =="4":
                print ("\n ¡Gracias por usar PCR Termophilic Cells!")
                break
            else :
                print ("    Opción no válida")

        except KeyboardInterrupt :
            print ("\n\n ¡Hasta luego!")
            break
        except Exception as e :
            print (f"    Error: {e}")

if __name__ =="__main__":
    main ()
