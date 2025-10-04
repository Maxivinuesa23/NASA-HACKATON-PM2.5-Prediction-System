# ========================================
# CONFIGURACIÓN PRINCIPAL DEL BACKEND
# Configuraciones centralizadas usando Pydantic Settings
# ========================================

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configuraciones de la aplicación"""
    
    # ========================================
    # CONFIGURACIÓN DEL SERVIDOR
    # ========================================
    
    # Información básica de la aplicación
    APP_NAME: str = "CloudBusters Air Quality API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración del servidor
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    
    # URLs permitidas para CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "https://cloudbusters.vercel.app",  # Si tienes Vercel
    ]
    
    # ========================================
    # CONFIGURACIÓN DE BASE DE DATOS
    # ========================================
    
    # Base de datos SQLite
    DATABASE_URL: str = "sqlite:///./cloudbusters.db"
    
    # ========================================
    # CONFIGURACIÓN DE MACHINE LEARNING
    # ========================================
    
    # Rutas de modelos y datos
    BASE_DIR: Path = Path(__file__).parent.parent
    MODEL_PATH: str = str(BASE_DIR / "models" / "air_quality_model.pkl")
    DATA_PATH: str = str(BASE_DIR / "data")
    LOGS_PATH: str = str(BASE_DIR / "logs")
    
    # Configuración del modelo
    MODEL_TYPE: str = "LSTM"  # LSTM, GRU, Dense, etc.
    SEQUENCE_LENGTH: int = 10  # Días de datos históricos para predicción
    FEATURES: List[str] = ["pm25", "no2"]  # Features del modelo
    
    # Parámetros de entrenamiento
    DEFAULT_EPOCHS: int = 100
    BATCH_SIZE: int = 32
    VALIDATION_SPLIT: float = 0.2
    RANDOM_STATE: int = 42
    
    # ========================================
    # CONFIGURACIÓN DE API EXTERNA
    # ========================================
    
    # APIs de calidad del aire (para datos reales)
    OPENWEATHER_API_KEY: Optional[str] = None
    AQICN_API_KEY: Optional[str] = None
    
    # URLs de APIs externas
    OPENWEATHER_BASE_URL: str = "http://api.openweathermap.org/data/2.5"
    AQICN_BASE_URL: str = "https://api.waqi.info"
    
    # ========================================
    # CONFIGURACIÓN DE LOGGING
    # ========================================
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "cloudbusters.log"
    
    # ========================================
    # CONFIGURACIÓN DE CACHÉ
    # ========================================
    
    # Tiempo de vida del caché (en segundos)
    CACHE_TTL_CITIES: int = 3600  # 1 hora
    CACHE_TTL_WEATHER: int = 300  # 5 minutos
    CACHE_TTL_PREDICTIONS: int = 1800  # 30 minutos
    
    # ========================================
    # CONFIGURACIÓN DE DATOS SINTÉTICOS
    # ========================================
    
    # Ciudades por defecto con datos base
    DEFAULT_CITIES: List[dict] = [
        {
            "name": "Mendoza",
            "country": "Argentina",
            "lat": -32.8895,
            "lon": -68.8458,
            "timezone": "America/Argentina/Mendoza",
            "base_pm25": 25.0,  # PM2.5 base para simulación
            "base_no2": 30.0,   # NO2 base para simulación
        },
        {
            "name": "Buenos Aires",
            "country": "Argentina", 
            "lat": -34.6118,
            "lon": -58.3960,
            "timezone": "America/Argentina/Buenos_Aires",
            "base_pm25": 35.0,
            "base_no2": 45.0,
        },
        {
            "name": "Córdoba",
            "country": "Argentina",
            "lat": -31.4201,
            "lon": -64.1888,
            "timezone": "America/Argentina/Cordoba",
            "base_pm25": 28.0,
            "base_no2": 35.0,
        },
        {
            "name": "Santiago",
            "country": "Chile",
            "lat": -33.4489,
            "lon": -70.6693,
            "timezone": "America/Santiago",
            "base_pm25": 55.0,
            "base_no2": 60.0,
        },
        {
            "name": "Lima",
            "country": "Peru",
            "lat": -12.0464,
            "lon": -77.0428,
            "timezone": "America/Lima",
            "base_pm25": 45.0,
            "base_no2": 50.0,
        }
    ]
    
    # ========================================
    # CONFIGURACIÓN DE VARIACIÓN DE DATOS
    # ========================================
    
    # Parámetros para generar variación realista en datos sintéticos
    PM25_VARIATION_RANGE: float = 0.3  # ±30% de variación
    NO2_VARIATION_RANGE: float = 0.25   # ±25% de variación
    SEASONAL_FACTOR: float = 0.15       # Factor estacional (15%)
    DAILY_PATTERN_FACTOR: float = 0.10  # Patrón diario (10%)
    
    # ========================================
    # CONFIGURACIÓN DE SEGURIDAD
    # ========================================
    
    # Secret key para JWT (si se implementa autenticación)
    SECRET_KEY: str = "cloudbusters-secret-key-change-in-production"
    
    # Rate limiting (requests por minuto)
    RATE_LIMIT_PREDICTIONS: int = 60
    RATE_LIMIT_GENERAL: int = 100
    
    # ========================================
    # CONFIGURACIÓN DE MODELO DE VALIDACIÓN
    # ========================================
    
    class Config:
        # Archivo .env para variables de entorno
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        # Ejemplos de variables de entorno
        env_prefix = "CLOUDBUSTERS_"

# ========================================
# INSTANCIA GLOBAL DE SETTINGS
# ========================================

# Crear instancia única de configuración
settings = Settings()

# ========================================
# FUNCIONES DE CONFIGURACIÓN
# ========================================

def get_settings() -> Settings:
    """Obtener instancia de configuración (para inyección de dependencias)"""
    return settings

def create_directories():
    """Crear directorios necesarios si no existen"""
    directories = [
        settings.DATA_PATH,
        settings.LOGS_PATH,
        Path(settings.MODEL_PATH).parent,
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def validate_config():
    """Validar configuración de la aplicación"""
    errors = []
    
    # Validar rutas críticas
    if not settings.BASE_DIR.exists():
        errors.append("Directorio base no existe")
    
    # Validar parámetros del modelo
    if settings.SEQUENCE_LENGTH < 1:
        errors.append("SEQUENCE_LENGTH debe ser mayor a 0")
    
    if settings.DEFAULT_EPOCHS < 1:
        errors.append("DEFAULT_EPOCHS debe ser mayor a 0")
    
    if not (0 < settings.VALIDATION_SPLIT < 1):
        errors.append("VALIDATION_SPLIT debe estar entre 0 y 1")
    
    # Validar configuración de red
    if not (1024 <= settings.PORT <= 65535):
        errors.append("PORT debe estar entre 1024 y 65535")
    
    if errors:
        raise ValueError(f"Errores de configuración: {', '.join(errors)}")
    
    return True

# ========================================
# CONFIGURACIONES DINÁMICAS
# ========================================

def get_model_config() -> dict:
    """Obtener configuración específica del modelo"""
    return {
        "sequence_length": settings.SEQUENCE_LENGTH,
        "features": settings.FEATURES,
        "model_type": settings.MODEL_TYPE,
        "batch_size": settings.BATCH_SIZE,
        "epochs": settings.DEFAULT_EPOCHS,
        "validation_split": settings.VALIDATION_SPLIT,
        "random_state": settings.RANDOM_STATE,
    }

def get_api_config() -> dict:
    """Obtener configuración de API"""
    return {
        "host": settings.HOST,
        "port": settings.PORT,
        "debug": settings.DEBUG,
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "rate_limits": {
            "predictions": settings.RATE_LIMIT_PREDICTIONS,
            "general": settings.RATE_LIMIT_GENERAL,
        }
    }

def get_cache_config() -> dict:
    """Obtener configuración de caché"""
    return {
        "cities_ttl": settings.CACHE_TTL_CITIES,
        "weather_ttl": settings.CACHE_TTL_WEATHER,
        "predictions_ttl": settings.CACHE_TTL_PREDICTIONS,
    }

# ========================================
# INICIALIZACIÓN
# ========================================

# Crear directorios al importar
create_directories()

# Validar configuración al importar
try:
    validate_config()
except ValueError as e:
    print(f"⚠️ Advertencia de configuración: {e}")

# Información de configuración para debug
if settings.DEBUG:
    print(f"🔧 CloudBusters configurado:")
    print(f"   - Host: {settings.HOST}:{settings.PORT}")
    print(f"   - Debug: {settings.DEBUG}")
    print(f"   - Base Dir: {settings.BASE_DIR}")
    print(f"   - Model Path: {settings.MODEL_PATH}")
    print(f"   - Database: {settings.DATABASE_URL}")