import mediapipe as mp
import numpy as np
from typing import Optional, List, Tuple, Dict


class HandDetector:
    """Detecta y rastrea manos usando MediaPipe."""
    
    def __init__(self, 
                 static_image_mode: bool = False,
                 max_num_hands: int = 2,
                 min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.5):
        """
        Inicializa el detector de manos.
        
        Args:
            static_image_mode: Si procesar como imagen estática o video
            max_num_hands: Número máximo de manos a detectar
            min_detection_confidence: Confianza mínima para detección
            min_tracking_confidence: Confianza mínima para tracking
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Landmarks importantes para interacción
        self.important_landmarks = {
            'wrist': 0,
            'thumb_tip': 4,
            'index_tip': 8,
            'middle_tip': 12,
            'ring_tip': 16,
            'pinky_tip': 20,
            'index_mcp': 5,  # Base del dedo índice
            'middle_mcp': 9,  # Base del dedo medio
        }
        
    def detect_hands(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detecta manos en una imagen.
        
        Args:
            image: Imagen en formato RGB
            
        Returns:
            Diccionario con información de las manos detectadas o None
        """
        try:
            results = self.hands.process(image)
            
            if results.multi_hand_landmarks:
                hands_data = []
                
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Información de la mano (izquierda/derecha)
                    handedness = results.multi_handedness[idx].classification[0].label
                    confidence = results.multi_handedness[idx].classification[0].score
                    
                    # Extraer coordenadas de landmarks importantes
                    landmarks = self._extract_landmarks(hand_landmarks, image.shape)
                    
                    # Calcular centro de la mano
                    center = self._calculate_hand_center(landmarks)
                    
                    # Calcular área aproximada de la mano
                    area = self._calculate_hand_area(landmarks)
                    
                    hand_data = {
                        'handedness': handedness,
                        'confidence': confidence,
                        'landmarks': landmarks,
                        'center': center,
                        'area': area,
                        'raw_landmarks': hand_landmarks
                    }
                    
                    hands_data.append(hand_data)
                
                return {
                    'hands': hands_data,
                    'num_hands': len(hands_data),
                    'timestamp': None  # Se puede agregar timestamp si es necesario
                }
            
            return None
            
        except Exception as e:
            print(f"Error detectando manos: {e}")
            return None
    
    def _extract_landmarks(self, hand_landmarks, image_shape) -> Dict[str, Tuple[float, float]]:
        """
        Extrae coordenadas normalizadas de landmarks importantes.
        
        Args:
            hand_landmarks: Landmarks de MediaPipe
            image_shape: Forma de la imagen (height, width, channels)
            
        Returns:
            Diccionario con coordenadas de landmarks importantes
        """
        height, width = image_shape[:2]
        landmarks = {}
        
        for name, idx in self.important_landmarks.items():
            landmark = hand_landmarks.landmark[idx]
            # Coordenadas normalizadas (0-1)
            x_norm = landmark.x
            y_norm = landmark.y
            
            # Coordenadas en píxeles
            x_pixel = int(x_norm * width)
            y_pixel = int(y_norm * height)
            
            landmarks[name] = {
                'normalized': (x_norm, y_norm),
                'pixel': (x_pixel, y_pixel)
            }
        
        return landmarks
    
    def _calculate_hand_center(self, landmarks: Dict) -> Tuple[float, float]:
        """
        Calcula el centro aproximado de la mano.
        
        Args:
            landmarks: Diccionario de landmarks
            
        Returns:
            Coordenadas normalizadas del centro (x, y)
        """
        if 'wrist' in landmarks and 'middle_mcp' in landmarks:
            wrist = landmarks['wrist']['normalized']
            middle_mcp = landmarks['middle_mcp']['normalized']
            
            # Centro entre muñeca y base del dedo medio
            center_x = (wrist[0] + middle_mcp[0]) / 2
            center_y = (wrist[1] + middle_mcp[1]) / 2
            
            return (center_x, center_y)
        
        return (0.5, 0.5)  # Centro de imagen por defecto
    
    def _calculate_hand_area(self, landmarks: Dict) -> float:
        """
        Calcula un área aproximada de la mano.
        
        Args:
            landmarks: Diccionario de landmarks
            
        Returns:
            Área aproximada normalizada
        """
        if 'wrist' in landmarks and 'middle_tip' in landmarks:
            wrist = landmarks['wrist']['normalized']
            middle_tip = landmarks['middle_tip']['normalized']
            
            # Distancia desde muñeca hasta punta del dedo medio
            dist = np.sqrt((middle_tip[0] - wrist[0])**2 + (middle_tip[1] - wrist[1])**2)
            
            # Área aproximada como círculo
            return np.pi * (dist / 2)**2
        
        return 0.01  # Área mínima por defecto
    
    def get_primary_hand_position(self, hands_data: Dict) -> Optional[Tuple[float, float]]:
        """
        Obtiene la posición de la mano principal (más confiable).
        
        Args:
            hands_data: Datos de manos detectadas
            
        Returns:
            Posición normalizada (x, y) de la mano principal o None
        """
        if hands_data and hands_data['num_hands'] > 0:
            # Seleccionar la mano con mayor confianza
            primary_hand = max(hands_data['hands'], key=lambda h: h['confidence'])
            return primary_hand['center']
        
        return None
    
    def draw_landmarks(self, image: np.ndarray, hands_data: Dict) -> np.ndarray:
        """
        Dibuja los landmarks de las manos en la imagen.
        
        Args:
            image: Imagen donde dibujar
            hands_data: Datos de manos detectadas
            
        Returns:
            Imagen con landmarks dibujados
        """
        if hands_data and hands_data['hands']:
            annotated_image = image.copy()
            
            for hand_data in hands_data['hands']:
                self.mp_drawing.draw_landmarks(
                    annotated_image,
                    hand_data['raw_landmarks'],
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Dibujar centro de la mano
                center = hand_data['center']
                height, width = image.shape[:2]
                center_pixel = (int(center[0] * width), int(center[1] * height))
                
                import cv2
                cv2.circle(annotated_image, center_pixel, 10, (255, 0, 0), -1)
            
            return annotated_image
        
        return image
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'hands'):
            self.hands.close() 