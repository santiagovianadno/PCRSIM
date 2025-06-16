import numpy as np
from typing import Tuple


def normalize_coordinates(x: float, y: float, width: int, height: int) -> Tuple[float, float]:
    """
    Normaliza coordenadas de píxeles a rango 0-1.
    
    Args:
        x, y: Coordenadas en píxeles
        width, height: Dimensiones de la imagen
        
    Returns:
        Coordenadas normalizadas (x, y)
    """
    norm_x = x / width if width > 0 else 0.0
    norm_y = y / height if height > 0 else 0.0
    
    # Asegurar que estén en el rango [0, 1]
    norm_x = max(0.0, min(1.0, norm_x))
    norm_y = max(0.0, min(1.0, norm_y))
    
    return norm_x, norm_y


def lerp(a: float, b: float, t: float) -> float:
    """
    Interpolación lineal entre dos valores.
    
    Args:
        a: Valor inicial
        b: Valor final
        t: Factor de interpolación (0-1)
        
    Returns:
        Valor interpolado
    """
    return a + t * (b - a)


def distance_2d(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calcula la distancia euclidiana entre dos puntos 2D.
    
    Args:
        point1: Primer punto (x, y)
        point2: Segundo punto (x, y)
        
    Returns:
        Distancia entre los puntos
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return np.sqrt(dx * dx + dy * dy)


def smooth_value(current: float, target: float, smoothing: float = 0.1) -> float:
    """
    Suaviza la transición entre valores usando interpolación exponencial.
    
    Args:
        current: Valor actual
        target: Valor objetivo
        smoothing: Factor de suavizado (0-1, más bajo = más suave)
        
    Returns:
        Valor suavizado
    """
    return current + (target - current) * smoothing


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limita un valor entre un mínimo y máximo.
    
    Args:
        value: Valor a limitar
        min_val: Valor mínimo
        max_val: Valor máximo
        
    Returns:
        Valor limitado
    """
    return max(min_val, min(max_val, value))


def map_range(value: float, 
              from_min: float, from_max: float,
              to_min: float, to_max: float) -> float:
    """
    Mapea un valor de un rango a otro.
    
    Args:
        value: Valor a mapear
        from_min, from_max: Rango original
        to_min, to_max: Rango destino
        
    Returns:
        Valor mapeado
    """
    # Normalizar el valor en el rango original
    normalized = (value - from_min) / (from_max - from_min)
    
    # Mapear al nuevo rango
    return to_min + normalized * (to_max - to_min)


def smooth_step(edge0: float, edge1: float, x: float) -> float:
    """
    Función de suavizado tipo Hermite.
    
    Args:
        edge0: Valor mínimo
        edge1: Valor máximo
        x: Valor de entrada
        
    Returns:
        Valor suavizado entre 0 y 1
    """
    # Clamp x to [0, 1]
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    
    # Interpolación suave
    return t * t * (3.0 - 2.0 * t)


class Vector2D:
    """Clase helper para operaciones con vectores 2D."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y
    
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def magnitude(self) -> float:
        return np.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self) -> 'Vector2D':
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y) 