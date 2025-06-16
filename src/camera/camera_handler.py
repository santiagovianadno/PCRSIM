import cv2
import numpy as np
from typing import Optional, Tuple


class CameraHandler:
    """Maneja la captura de video desde la cámara web."""
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """
        Inicializa el manejador de cámara.
        
        Args:
            camera_id: ID de la cámara (0 por defecto)
            width: Ancho del frame
            height: Alto del frame
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """
        Inicializa la captura de cámara.
        
        Returns:
            True si se inicializó correctamente, False si no
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"Error: No se pudo abrir la cámara {self.camera_id}")
                return False
                
            # Configurar resolución
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Configurar FPS
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_initialized = True
            print(f"Cámara inicializada: {self.width}x{self.height}")
            return True
            
        except Exception as e:
            print(f"Error inicializando cámara: {e}")
            return False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Captura un frame de la cámara.
        
        Returns:
            Imagen como array de numpy o None si hay error
        """
        if not self.is_initialized or self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        # Voltear horizontalmente para efecto espejo
        frame = cv2.flip(frame, 1)
        return frame
    
    def get_frame_rgb(self) -> Optional[np.ndarray]:
        """
        Captura un frame y lo convierte a RGB.
        
        Returns:
            Imagen en formato RGB o None si hay error
        """
        frame = self.get_frame()
        if frame is not None:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None
    
    def get_camera_info(self) -> Tuple[int, int]:
        """
        Obtiene información de la cámara.
        
        Returns:
            Tupla con (ancho, alto)
        """
        return self.width, self.height
    
    def release(self) -> None:
        """Libera los recursos de la cámara."""
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
            print("Cámara liberada")
    
    def __del__(self):
        """Destructor para asegurar liberación de recursos."""
        self.release() 