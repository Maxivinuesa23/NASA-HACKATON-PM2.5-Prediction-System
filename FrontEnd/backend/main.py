# ========================================
# BACKEND CLOUDBUSTERS - API PRINCIPAL
# FastAPI server para predicción de calidad del aire
# ========================================

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime
import os
from typing import List, Dict, Any, Optional
import json

# Imports internos
from models.air_quality_model import AirQualityModel
from services.data_service import DataService
from services.prediction_service import PredictionService
from schemas.api_schemas import (
    PredictionRequest,
    PredictionResponse,
    CityDataResponse,
    HealthResponse,
    CitiesResponse,
    TimeSeriesResponse,
    TrainingRequest
)
from core.config import settings
from core.logging_config import setup_logging
from database.database import engine, create_tables

# ========================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ========================================

# Setup logging
logger = setup_logging()

# Crear tablas de base de datos
create_tables()

# Crear instancia de FastAPI
app = FastAPI(
    title="CloudBusters Air Quality API",
    description="API para predicción de calidad del aire utilizando Machine Learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# SERVICIOS GLOBALES
# ========================================

# Instancias de servicios
data_service = DataService()
prediction_service = PredictionService()
model = AirQualityModel()

# ========================================
# EVENTOS DE APLICACIÓN
# ========================================

@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al arrancar la aplicación"""
    logger.info("🚀 Iniciando CloudBusters API...")
    
    try:
        # Cargar modelo si existe
        if os.path.exists(settings.MODEL_PATH):
            logger.info("📦 Cargando modelo preentrenado...")
            model.load_model(settings.MODEL_PATH)
            logger.info("✅ Modelo cargado exitosamente")
        else:
            logger.warning("⚠️ No se encontró modelo preentrenado. Se entrenará uno nuevo.")
            
        # Inicializar datos base
        await data_service.initialize_cities()
        logger.info("✅ Datos iniciales cargados")
        
        logger.info("🎉 CloudBusters API iniciada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante el startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar la aplicación"""
    logger.info("👋 Cerrando CloudBusters API...")

# ========================================
# ENDPOINTS DE SALUD Y ESTADO
# ========================================

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Endpoint para verificar el estado del servidor y modelo"""
    try:
        model_status = model.is_loaded()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            model_loaded=model_status,
            version="1.0.0",
            device=model.device if model_status else "N/A",
            message="CloudBusters API funcionando correctamente"
        )
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "🌍 CloudBusters Air Quality API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "description": "API para predicción de calidad del aire"
    }

# ========================================
# ENDPOINTS DE CIUDADES
# ========================================

@app.get("/api/cities", response_model=CitiesResponse)
async def get_cities():
    """Obtener lista de ciudades disponibles"""
    try:
        cities_data = await data_service.get_cities()
        
        return CitiesResponse(
            success=True,
            data=cities_data,
            message=f"Se encontraron {len(cities_data.get('cities', []))} ciudades"
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo ciudades: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo ciudades: {str(e)}")

@app.get("/api/cities/{city_name}", response_model=CityDataResponse)
async def get_city_data(city_name: str):
    """Obtener datos actuales de una ciudad específica"""
    try:
        city_data = await data_service.get_city_current_data(city_name)
        
        if not city_data:
            raise HTTPException(status_code=404, detail=f"Ciudad '{city_name}' no encontrada")
        
        return CityDataResponse(
            success=True,
            data=city_data,
            city=city_name,
            message=f"Datos actuales de {city_name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo datos de {city_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos de ciudad: {str(e)}")

# ========================================
# ENDPOINTS DE PREDICCIÓN
# ========================================

@app.post("/api/predict", response_model=PredictionResponse)
async def make_prediction(request: PredictionRequest):
    """Realizar predicción de PM2.5 basada en secuencia de datos"""
    try:
        if not model.is_loaded():
            raise HTTPException(status_code=503, detail="Modelo no disponible. Entrene el modelo primero.")
        
        # Validar datos de entrada
        if len(request.sequence) != 10:
            raise HTTPException(status_code=400, detail="La secuencia debe tener exactamente 10 días de datos")
        
        for i, day_data in enumerate(request.sequence):
            if len(day_data) != 2:
                raise HTTPException(status_code=400, detail=f"Día {i+1}: debe tener exactamente 2 valores [PM2.5, NO2]")
        
        # Realizar predicción
        prediction_result = await prediction_service.make_prediction(
            sequence=request.sequence,
            model=model
        )
        
        return PredictionResponse(
            success=True,
            prediction=prediction_result,
            input_data={
                "sequence_length": len(request.sequence),
                "last_pm25": request.sequence[-1][0],
                "last_no2": request.sequence[-1][1]
            },
            message="Predicción realizada exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error realizando predicción: {str(e)}")

@app.post("/api/predict/city/{city_name}")
async def predict_for_city(city_name: str):
    """Realizar predicción automática para una ciudad usando sus datos históricos"""
    try:
        if not model.is_loaded():
            raise HTTPException(status_code=503, detail="Modelo no disponible. Entrene el modelo primero.")
        
        # Obtener datos históricos de la ciudad
        time_series_data = await data_service.get_city_time_series(city_name, days=10)
        
        if not time_series_data or not time_series_data.get('sequences'):
            raise HTTPException(status_code=404, detail=f"No hay suficientes datos históricos para {city_name}")
        
        # Usar la última secuencia disponible
        last_sequence = time_series_data['sequences'][-1]
        
        # Realizar predicción
        prediction_result = await prediction_service.make_prediction(
            sequence=last_sequence,
            model=model
        )
        
        return {
            "success": True,
            "prediction": prediction_result,
            "city": city_name,
            "based_on": {
                "data_points": time_series_data.get('total_points', 0),
                "date_range": f"{time_series_data.get('dates', ['N/A'])[0]} - {time_series_data.get('dates', ['N/A'])[-1]}"
            },
            "message": f"Predicción para {city_name} realizada exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en predicción para {city_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en predicción para ciudad: {str(e)}")

# ========================================
# ENDPOINTS DE ENTRENAMIENTO
# ========================================

@app.post("/api/train")
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Entrenar o reentrenar el modelo de predicción"""
    try:
        # Validar parámetros
        if request.city and not await data_service.city_exists(request.city):
            raise HTTPException(status_code=404, detail=f"Ciudad '{request.city}' no encontrada")
        
        # Agregar tarea de entrenamiento en background
        background_tasks.add_task(
            _train_model_background,
            city=request.city,
            retrain=request.retrain,
            epochs=request.epochs
        )
        
        return {
            "success": True,
            "message": f"Entrenamiento iniciado para {request.city or 'todas las ciudades'}",
            "status": "training_started",
            "parameters": {
                "city": request.city,
                "retrain": request.retrain,
                "epochs": request.epochs
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error iniciando entrenamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error iniciando entrenamiento: {str(e)}")

async def _train_model_background(city: Optional[str] = None, retrain: bool = True, epochs: int = 100):
    """Función para entrenar el modelo en background"""
    try:
        logger.info(f"🎯 Iniciando entrenamiento para {city or 'todas las ciudades'}")
        
        # Obtener datos de entrenamiento
        training_data = await data_service.get_training_data(city)
        
        if not training_data:
            logger.error("No se encontraron datos para entrenamiento")
            return
        
        # Entrenar modelo
        training_result = await prediction_service.train_model(
            training_data=training_data,
            model=model,
            retrain=retrain,
            epochs=epochs
        )
        
        # Guardar modelo entrenado
        model.save_model(settings.MODEL_PATH)
        
        logger.info(f"✅ Entrenamiento completado: {training_result}")
        
    except Exception as e:
        logger.error(f"❌ Error en entrenamiento background: {str(e)}")

# ========================================
# ENDPOINTS DE DATOS HISTÓRICOS
# ========================================

@app.get("/api/generate-data/{city_name}", response_model=TimeSeriesResponse)
async def get_time_series_data(city_name: str, days: int = 30):
    """Generar datos de serie temporal para una ciudad"""
    try:
        if days < 1 or days > 365:
            raise HTTPException(status_code=400, detail="Los días deben estar entre 1 y 365")
        
        time_series_data = await data_service.get_city_time_series(city_name, days)
        
        if not time_series_data:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para {city_name}")
        
        return TimeSeriesResponse(
            success=True,
            data=time_series_data,
            city=city_name,
            days_requested=days,
            message=f"Serie temporal de {days} días para {city_name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando serie temporal para {city_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando datos: {str(e)}")

# ========================================
# ENDPOINTS DE ADMINISTRACIÓN
# ========================================

@app.get("/api/admin/model-info")
async def get_model_info():
    """Obtener información detallada del modelo"""
    try:
        info = model.get_model_info()
        return {
            "success": True,
            "model_info": info,
            "message": "Información del modelo obtenida"
        }
    except Exception as e:
        logger.error(f"Error obteniendo info del modelo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/clear-cache")
async def clear_cache():
    """Limpiar caché de datos"""
    try:
        await data_service.clear_cache()
        return {
            "success": True,
            "message": "Caché limpiado exitosamente"
        }
    except Exception as e:
        logger.error(f"Error limpiando caché: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# MANEJO DE ERRORES GLOBALES
# ========================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado",
            "details": str(exc) if settings.DEBUG else "Error interno"
        }
    )

# ========================================
# EJECUCIÓN PRINCIPAL
# ========================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )