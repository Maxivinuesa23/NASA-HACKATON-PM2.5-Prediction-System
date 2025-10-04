# ========================================
# ESQUEMAS PYDANTIC PARA API
# Definición de modelos de entrada y salida de la API
# ========================================

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# ========================================
# ENUMS Y TIPOS
# ========================================

class AirQualityCategory(str, Enum):
    """Categorías de calidad del aire según PM2.5"""
    GOOD = "good"
    MODERATE = "moderate"
    UNHEALTHY_SENSITIVE = "unhealthy_for_sensitive"
    UNHEALTHY = "unhealthy"
    VERY_UNHEALTHY = "very_unhealthy"
    HAZARDOUS = "hazardous"

class ModelStatus(str, Enum):
    """Estados del modelo de ML"""
    LOADED = "loaded"
    NOT_LOADED = "not_loaded"
    TRAINING = "training"
    ERROR = "error"

# ========================================
# ESQUEMAS BASE
# ========================================

class BaseResponse(BaseModel):
    """Esquema base para todas las respuestas"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    message: str = Field(..., description="Mensaje descriptivo de la respuesta")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())

class ErrorResponse(BaseResponse):
    """Esquema para respuestas de error"""
    success: bool = False
    error: str = Field(..., description="Tipo de error")
    details: Optional[str] = Field(None, description="Detalles adicionales del error")

# ========================================
# ESQUEMAS DE ENTRADA (REQUESTS)
# ========================================

class PredictionRequest(BaseModel):
    """Esquema para solicitudes de predicción"""
    sequence: List[List[float]] = Field(
        ..., 
        description="Secuencia de 10 días con valores [PM2.5, NO2]",
        min_items=10,
        max_items=10
    )
    
    @validator('sequence')
    def validate_sequence(cls, v):
        """Validar que cada día tenga exactamente 2 valores"""
        for i, day in enumerate(v):
            if len(day) != 2:
                raise ValueError(f"Día {i+1} debe tener exactamente 2 valores [PM2.5, NO2]")
            if any(not isinstance(val, (int, float)) for val in day):
                raise ValueError(f"Día {i+1} debe contener solo valores numéricos")
            if any(val < 0 for val in day):
                raise ValueError(f"Día {i+1} no puede tener valores negativos")
        return v

class TrainingRequest(BaseModel):
    """Esquema para solicitudes de entrenamiento"""
    city: Optional[str] = Field(None, description="Ciudad específica para entrenar (opcional)")
    retrain: bool = Field(True, description="Si reentrenar desde cero o continuar")
    epochs: int = Field(100, description="Número de épocas de entrenamiento", ge=1, le=1000)
    
class CityRequest(BaseModel):
    """Esquema para solicitudes relacionadas con ciudades"""
    name: str = Field(..., description="Nombre de la ciudad")
    country: Optional[str] = Field(None, description="País de la ciudad")

# ========================================
# ESQUEMAS DE DATOS
# ========================================

class CityData(BaseModel):
    """Datos de calidad del aire de una ciudad"""
    pm25: Optional[float] = Field(None, description="Concentración de PM2.5 en μg/m³", ge=0)
    no2: Optional[float] = Field(None, description="Concentración de NO2 en μg/m³", ge=0)
    aqi: Optional[int] = Field(None, description="Índice de calidad del aire", ge=0, le=500)
    temperature: Optional[float] = Field(None, description="Temperatura en Celsius")
    humidity: Optional[float] = Field(None, description="Humedad relativa en %", ge=0, le=100)
    wind_speed: Optional[float] = Field(None, description="Velocidad del viento en km/h", ge=0)
    pressure: Optional[float] = Field(None, description="Presión atmosférica en hPa", ge=800, le=1200)
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())

class CityInfo(BaseModel):
    """Información básica de una ciudad"""
    name: str = Field(..., description="Nombre de la ciudad")
    country: str = Field(..., description="País")
    lat: float = Field(..., description="Latitud", ge=-90, le=90)
    lon: float = Field(..., description="Longitud", ge=-180, le=180)
    timezone: Optional[str] = Field(None, description="Zona horaria")
    population: Optional[int] = Field(None, description="Población aproximada", ge=0)

class PredictionResult(BaseModel):
    """Resultado de una predicción"""
    pm25_predicted: float = Field(..., description="Valor de PM2.5 predicho", ge=0)
    confidence: Optional[float] = Field(None, description="Nivel de confianza (0-1)", ge=0, le=1)
    prediction_for: str = Field(..., description="Fecha para la cual se predice")
    model_version: Optional[str] = Field(None, description="Versión del modelo usado")
    features_used: Optional[List[str]] = Field(None, description="Features utilizadas en la predicción")

class TimeSeriesData(BaseModel):
    """Datos de serie temporal"""
    dates: List[str] = Field(..., description="Fechas de los datos")
    targets: List[float] = Field(..., description="Valores objetivo (PM2.5)")
    features: Optional[List[List[float]]] = Field(None, description="Features adicionales")
    sequences: Optional[List[List[List[float]]]] = Field(None, description="Secuencias para ML")
    total_points: int = Field(..., description="Total de puntos de datos", ge=0)

class ModelInfo(BaseModel):
    """Información del modelo de ML"""
    model_type: str = Field(..., description="Tipo de modelo (LSTM, GRU, etc.)")
    is_loaded: bool = Field(..., description="Si el modelo está cargado")
    features: List[str] = Field(..., description="Features del modelo")
    sequence_length: int = Field(..., description="Longitud de secuencia", ge=1)
    last_trained: Optional[str] = Field(None, description="Última fecha de entrenamiento")
    accuracy_metrics: Optional[Dict[str, float]] = Field(None, description="Métricas de precisión")
    device: Optional[str] = Field(None, description="Dispositivo usado (CPU/GPU)")

# ========================================
# ESQUEMAS DE RESPUESTA (RESPONSES)
# ========================================

class HealthResponse(BaseResponse):
    """Respuesta del endpoint de salud"""
    status: str = Field(..., description="Estado del servidor")
    model_loaded: bool = Field(..., description="Si el modelo está cargado")
    version: str = Field(..., description="Versión de la API")
    device: Optional[str] = Field(None, description="Dispositivo del modelo")

class CitiesResponse(BaseResponse):
    """Respuesta con lista de ciudades"""
    data: Dict[str, Any] = Field(..., description="Datos de ciudades")
    total_cities: Optional[int] = Field(None, description="Total de ciudades disponibles")

class CityDataResponse(BaseResponse):
    """Respuesta con datos de una ciudad"""
    data: CityData = Field(..., description="Datos de calidad del aire")
    city: str = Field(..., description="Nombre de la ciudad")
    air_quality_category: Optional[Dict[str, str]] = Field(None, description="Categoría de calidad del aire")

class PredictionResponse(BaseResponse):
    """Respuesta de predicción"""
    prediction: PredictionResult = Field(..., description="Resultado de la predicción")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Datos de entrada utilizados")
    processing_time: Optional[float] = Field(None, description="Tiempo de procesamiento en segundos")

class TimeSeriesResponse(BaseResponse):
    """Respuesta con datos de serie temporal"""
    data: TimeSeriesData = Field(..., description="Datos de serie temporal")
    city: str = Field(..., description="Ciudad de los datos")
    days_requested: int = Field(..., description="Días solicitados", ge=1)

class TrainingResponse(BaseResponse):
    """Respuesta de entrenamiento"""
    training_id: Optional[str] = Field(None, description="ID del entrenamiento")
    status: str = Field(..., description="Estado del entrenamiento")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parámetros de entrenamiento")
    estimated_duration: Optional[str] = Field(None, description="Duración estimada")

class ModelInfoResponse(BaseResponse):
    """Respuesta con información del modelo"""
    model_info: ModelInfo = Field(..., description="Información detallada del modelo")

# ========================================
# ESQUEMAS COMPUESTOS
# ========================================

class DashboardData(BaseModel):
    """Datos completos para dashboard"""
    current_data: CityData = Field(..., description="Datos actuales")
    time_series: TimeSeriesData = Field(..., description="Serie temporal")
    latest_prediction: Optional[PredictionResult] = Field(None, description="Última predicción")
    air_quality_trend: Optional[str] = Field(None, description="Tendencia de calidad del aire")

class DashboardResponse(BaseResponse):
    """Respuesta completa del dashboard"""
    data: DashboardData = Field(..., description="Datos del dashboard")
    city: str = Field(..., description="Ciudad del dashboard")
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

class BatchPredictionRequest(BaseModel):
    """Solicitud de predicción para múltiples ciudades"""
    cities: List[str] = Field(..., description="Lista de ciudades", min_items=1, max_items=10)
    days_back: int = Field(10, description="Días hacia atrás para datos", ge=1, le=30)

class BatchPredictionResponse(BaseResponse):
    """Respuesta de predicción por lotes"""
    predictions: Dict[str, Union[PredictionResult, str]] = Field(
        ..., 
        description="Predicciones por ciudad (resultado o error)"
    )
    successful_predictions: int = Field(..., description="Número de predicciones exitosas")
    failed_predictions: int = Field(..., description="Número de predicciones fallidas")

# ========================================
# ESQUEMAS DE CONFIGURACIÓN
# ========================================

class APIConfig(BaseModel):
    """Configuración de la API"""
    version: str = Field(..., description="Versión de la API")
    features_enabled: List[str] = Field(..., description="Features habilitadas")
    rate_limits: Dict[str, int] = Field(..., description="Límites de rate")
    supported_cities: List[str] = Field(..., description="Ciudades soportadas")

class ConfigResponse(BaseResponse):
    """Respuesta con configuración de la API"""
    config: APIConfig = Field(..., description="Configuración actual")

# ========================================
# UTILIDADES DE VALIDACIÓN
# ========================================

def validate_pm25_value(value: float) -> float:
    """Validar valor de PM2.5"""
    if value < 0:
        raise ValueError("PM2.5 no puede ser negativo")
    if value > 1000:
        raise ValueError("PM2.5 parece ser demasiado alto (>1000)")
    return value

def validate_city_name(name: str) -> str:
    """Validar nombre de ciudad"""
    if not name or not name.strip():
        raise ValueError("Nombre de ciudad no puede estar vacío")
    if len(name.strip()) < 2:
        raise ValueError("Nombre de ciudad debe tener al menos 2 caracteres")
    return name.strip().title()

# ========================================
# EJEMPLOS PARA DOCUMENTACIÓN
# ========================================

class Examples:
    """Ejemplos para la documentación de la API"""
    
    PREDICTION_REQUEST = {
        "sequence": [
            [25.5, 30.2],  # Día 1: PM2.5=25.5, NO2=30.2
            [27.1, 32.1],  # Día 2
            [24.8, 29.5],  # Día 3
            [26.3, 31.0],  # Día 4
            [28.9, 33.5],  # Día 5
            [25.2, 30.8],  # Día 6
            [23.7, 28.9],  # Día 7
            [26.8, 32.2],  # Día 8
            [29.1, 34.1],  # Día 9
            [27.4, 31.7]   # Día 10
        ]
    }
    
    PREDICTION_RESPONSE = {
        "success": True,
        "message": "Predicción realizada exitosamente",
        "timestamp": "2024-01-15T10:30:00",
        "prediction": {
            "pm25_predicted": 28.5,
            "confidence": 0.87,
            "prediction_for": "2024-01-16",
            "model_version": "1.0.0",
            "features_used": ["pm25", "no2"]
        },
        "input_data": {
            "sequence_length": 10,
            "last_pm25": 27.4,
            "last_no2": 31.7
        },
        "processing_time": 0.156
    }