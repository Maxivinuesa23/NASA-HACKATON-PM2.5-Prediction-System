# ========================================
# CONFIGURACIÓN DE LOGGING
# Setup centralizado para logs de la aplicación
# ========================================

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
import structlog
from core.config import settings

def setup_logging() -> logging.Logger:
    """
    Configurar sistema de logging para la aplicación
    
    Returns:
        logging.Logger: Logger configurado para la aplicación
    """
    
    # Crear directorio de logs si no existe
    Path(settings.LOGS_PATH).mkdir(parents=True, exist_ok=True)
    
    # Configurar logging básico
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=settings.LOG_FORMAT,
        handlers=[
            # Handler para consola
            logging.StreamHandler(sys.stdout),
            # Handler para archivo con rotación
            logging.handlers.RotatingFileHandler(
                filename=Path(settings.LOGS_PATH) / settings.LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )
    
    # Configurar structlog para logs estructurados
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Crear logger principal
    logger = logging.getLogger("cloudbusters")
    
    # Configurar niveles de logging para librerías externas
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("tensorflow").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logger

def get_api_logger() -> logging.Logger:
    """Obtener logger específico para API requests"""
    return logging.getLogger("cloudbusters.api")

def get_model_logger() -> logging.Logger:
    """Obtener logger específico para operaciones de ML"""
    return logging.getLogger("cloudbusters.model")

def get_data_logger() -> logging.Logger:
    """Obtener logger específico para operaciones de datos"""
    return logging.getLogger("cloudbusters.data")

def log_request(logger: logging.Logger, method: str, path: str, status_code: int, duration: float):
    """
    Log de request HTTP con información relevante
    
    Args:
        logger: Logger a usar
        method: Método HTTP (GET, POST, etc.)
        path: Path del endpoint
        status_code: Código de respuesta HTTP
        duration: Duración en segundos
    """
    logger.info(
        f"{method} {path} - {status_code} - {duration:.3f}s",
        extra={
            "http_method": method,
            "path": path,
            "status_code": status_code,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }
    )

def log_model_operation(logger: logging.Logger, operation: str, details: dict):
    """
    Log de operaciones de machine learning
    
    Args:
        logger: Logger a usar
        operation: Tipo de operación (train, predict, load, save)
        details: Detalles de la operación
    """
    logger.info(
        f"Model {operation}: {details.get('message', 'completed')}",
        extra={
            "operation": operation,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
    )

def log_data_operation(logger: logging.Logger, operation: str, entity: str, details: dict = None):
    """
    Log de operaciones de datos
    
    Args:
        logger: Logger a usar
        operation: Tipo de operación (fetch, cache, generate)
        entity: Entidad afectada (city, weather, etc.)
        details: Detalles adicionales
    """
    logger.info(
        f"Data {operation} for {entity}",
        extra={
            "operation": operation,
            "entity": entity,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    )