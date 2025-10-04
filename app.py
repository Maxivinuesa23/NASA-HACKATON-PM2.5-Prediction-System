# ========================================
# API FLASK PARA PREDICTOR DE CALIDAD DEL AIRE
# Backend REST API que mantiene toda la funcionalidad original
# Compatible con frontend React
# ========================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import torch
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# CONFIGURAR RUTA DE IMPORTACIONES
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# IMPORTAR FUNCIONALIDAD ORIGINAL (SIN MODIFICAR)
from AirVisualSimulator import (
    generate_airvisual_data, 
    AirQualityDataset, 
    SEQ_LENGTH, 
    N_FEATURES, 
    SCALER, 
    CITIES,
    aqi_to_pm25,
    get_aqi_quality_level
)
from ModeloLSTM import (
    AirQualityPredictor, 
    train_model, 
    make_single_prediction, 
    HIDDEN_DIM, 
    NUM_LAYERS, 
    OUTPUT_DIM, 
    BATCH_SIZE, 
    DROPOUT_RATE,
    DEVICE
)

# CONFIGURACIÓN FLASK
app = Flask(__name__)
CORS(app)  # Permitir peticiones desde React

# CONFIGURACIÓN GLOBAL
MODEL_PATH = 'air_quality_predictor_model.pth'
model = None  # Variable global para el modelo
cached_data = {}  # Cache para datos de ciudades

def initialize_model():
    """
    FUNCIÓN: Inicializa y carga el modelo LSTM
    PROPÓSITO: Preparar modelo para hacer predicciones
    """
    global model
    print("🧠 Inicializando modelo LSTM...")
    
    try:
        model = AirQualityPredictor(N_FEATURES, HIDDEN_DIM, NUM_LAYERS, OUTPUT_DIM, DROPOUT_RATE)
        
        # Intentar cargar modelo pre-entrenado
        if os.path.exists(MODEL_PATH):
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
            print("✅ Modelo cargado exitosamente")
        else:
            print("⚠️ Modelo no encontrado, será entrenado cuando sea necesario")
            
        return True
    except Exception as e:
        print(f"❌ Error inicializando modelo: {e}")
        return False

def ensure_model_trained(city_data):
    """
    FUNCIÓN: Asegura que el modelo esté entrenado con datos de la ciudad
    PROPÓSITO: Entrenar modelo si no existe o si es necesario
    """
    global model
    
    if not os.path.exists(MODEL_PATH):
        print("🔄 Entrenando modelo con datos actuales...")
        
        try:
            # Crear dataset con los datos
            from torch.utils.data import DataLoader, random_split
            
            full_dataset = AirQualityDataset(city_data, SEQ_LENGTH)
            
            # Dividir datos
            train_size = int(0.8 * len(full_dataset))
            val_size = len(full_dataset) - train_size
            train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
            
            # Crear DataLoaders
            train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
            
            # Entrenar modelo
            train_model(model, train_loader, val_loader)
            
            # Guardar modelo
            torch.save(model.state_dict(), MODEL_PATH)
            print("💾 Modelo entrenado y guardado")
            
        except Exception as e:
            print(f"❌ Error entrenando modelo: {e}")
            return False
    
    return True

def predict_next_day_pm25(city_info):
    """
    FUNCIÓN: Predice PM2.5 para el día siguiente
    PROPÓSITO: Usar modelo LSTM para generar predicción
    """
    try:
        # Obtener datos de la ciudad
        city_data = generate_airvisual_data(city_info)
        
        if city_data is None or len(city_data) < SEQ_LENGTH + 10:
            return None
            
        # Asegurar que el modelo esté entrenado
        if not ensure_model_trained(city_data):
            return None
            
        # Crear dataset y obtener última secuencia
        full_dataset = AirQualityDataset(city_data, SEQ_LENGTH)
        last_sequence_data, _ = full_dataset[len(full_dataset)-1]
        prediction_sequence = last_sequence_data.cpu().numpy()
        
        # Hacer predicción
        predicted_pm25 = make_single_prediction(model, prediction_sequence)
        
        # Obtener valor actual para comparación
        if SCALER is not None:
            last_pm25_scaled = full_dataset.data[-1][0].item()
            mean_pm25 = SCALER.mean_[0]
            scale_pm25 = SCALER.scale_[0]
            current_pm25 = (last_pm25_scaled * scale_pm25) + mean_pm25
        else:
            current_pm25 = 25.0
            
        return {
            'current_pm25': round(current_pm25, 1),
            'predicted_pm25': round(predicted_pm25, 1),
            'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'confidence': 0.85  # Placeholder para confianza
        }
        
    except Exception as e:
        print(f"❌ Error en predicción: {e}")
        return None

# ========================================
# ENDPOINTS DE LA API
# ========================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    ENDPOINT: Estado del servidor
    RETORNA: JSON con estado de salud del sistema
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Predictor de Calidad del Aire API funcionando',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'device': str(DEVICE)
    })

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """
    ENDPOINT: Lista de ciudades disponibles
    RETORNA: JSON con todas las ciudades que se pueden consultar
    """
    cities_list = []
    for key, city in CITIES.items():
        cities_list.append({
            'id': key,
            'name': city['name'],
            'city': city['city'],
            'state': city['state'],
            'country': city['country']
        })
    
    return jsonify({
        'success': True,
        'cities': cities_list,
        'total': len(cities_list)
    })

@app.route('/api/cities/<city_name>', methods=['GET'])
def get_city_data(city_name):
    """
    ENDPOINT: Datos actuales de una ciudad específica
    PARÁMETRO: city_name (nombre de la ciudad)
    RETORNA: JSON con datos actuales y predicción
    """
    try:
        # Buscar ciudad en el diccionario
        selected_city = None
        for key, city in CITIES.items():
            if city['name'].lower() == city_name.lower() or city['city'].lower() == city_name.lower():
                selected_city = city
                break
        
        if not selected_city:
            return jsonify({
                'success': False,
                'message': f'Ciudad "{city_name}" no encontrada'
            }), 404
        
        # Verificar cache
        cache_key = f"city_{selected_city['name']}"
        if cache_key in cached_data:
            cache_time = cached_data[cache_key]['timestamp']
            if (datetime.now() - cache_time).seconds < 300:  # Cache de 5 minutos
                return jsonify(cached_data[cache_key]['data'])
        
        # Obtener datos actuales
        city_data = generate_airvisual_data(selected_city)
        
        if city_data is None:
            return jsonify({
                'success': False,
                'message': 'No se pudieron obtener datos para la ciudad'
            }), 500
        
        # Obtener última fila de datos
        latest_data = city_data.iloc[-1]
        
        # Simular datos meteorológicos adicionales
        weather_data = {
            'temperature': round(np.random.normal(22, 8), 1),  # Temperatura simulada
            'humidity': round(np.random.normal(60, 20), 1),    # Humedad simulada
            'wind_speed': round(np.random.normal(15, 5), 1),   # Viento simulado
            'pressure': round(np.random.normal(1013, 20), 1)   # Presión simulada
        }
        
        # Convertir PM2.5 a AQI para clasificación
        pm25_value = latest_data['PM2.5']
        aqi_approx = min(500, max(0, pm25_value * 2))  # Aproximación simple
        quality_level, quality_emoji = get_aqi_quality_level(aqi_approx)
        
        # Obtener predicción
        prediction = predict_next_day_pm25(selected_city)
        
        response_data = {
            'success': True,
            'city': selected_city['name'],
            'timestamp': datetime.now().isoformat(),
            'data': {
                'current': {
                    'pm25': round(pm25_value, 1),
                    'no2': round(latest_data['NO2'], 1),
                    'aqi': round(aqi_approx, 0),
                    'quality_level': quality_level,
                    'quality_emoji': quality_emoji,
                    'weather': weather_data
                },
                'prediction': prediction if prediction else {
                    'current_pm25': round(pm25_value, 1),
                    'predicted_pm25': round(pm25_value * 0.95, 1),
                    'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'confidence': 0.75
                }
            }
        }
        
        # Guardar en cache
        cached_data[cache_key] = {
            'data': response_data,
            'timestamp': datetime.now()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo datos: {str(e)}'
        }), 500

@app.route('/api/predict', methods=['POST'])
def predict_city():
    """
    ENDPOINT: Predicción específica para una ciudad
    MÉTODO: POST con JSON body {'city': 'nombre_ciudad'}
    RETORNA: JSON con predicción detallada
    """
    try:
        data = request.get_json()
        
        if not data or 'city' not in data:
            return jsonify({
                'success': False,
                'message': 'Falta especificar la ciudad en el JSON'
            }), 400
        
        city_name = data['city']
        
        # Buscar ciudad
        selected_city = None
        for key, city in CITIES.items():
            if city['name'].lower() == city_name.lower():
                selected_city = city
                break
        
        if not selected_city:
            return jsonify({
                'success': False,
                'message': f'Ciudad "{city_name}" no encontrada'
            }), 404
        
        # Obtener predicción
        prediction = predict_next_day_pm25(selected_city)
        
        if not prediction:
            return jsonify({
                'success': False,
                'message': 'No se pudo generar predicción'
            }), 500
        
        return jsonify({
            'success': True,
            'city': selected_city['name'],
            'prediction': prediction,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en predicción: {str(e)}'
        }), 500

@app.route('/api/train', methods=['POST'])
def train_model_endpoint():
    """
    ENDPOINT: Forzar re-entrenamiento del modelo
    MÉTODO: POST con JSON body {'city': 'nombre_ciudad'}
    RETORNA: JSON con resultado del entrenamiento
    """
    try:
        data = request.get_json()
        city_name = data.get('city', 'Ciudad de México')
        
        # Buscar ciudad
        selected_city = CITIES.get("1")  # Default a Ciudad de México
        for key, city in CITIES.items():
            if city['name'].lower() == city_name.lower():
                selected_city = city
                break
        
        # Eliminar modelo actual para forzar re-entrenamiento
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        
        # Obtener datos y entrenar
        city_data = generate_airvisual_data(selected_city)
        
        if city_data is None:
            return jsonify({
                'success': False,
                'message': 'No se pudieron obtener datos para entrenamiento'
            }), 500
        
        success = ensure_model_trained(city_data)
        
        return jsonify({
            'success': success,
            'message': 'Modelo re-entrenado exitosamente' if success else 'Error en entrenamiento',
            'city': selected_city['name'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en entrenamiento: {str(e)}'
        }), 500

@app.route('/api/generate-data/<city_name>', methods=['GET'])
def generate_city_data(city_name):
    """
    ENDPOINT: Generar nueva serie temporal para una ciudad
    PARÁMETRO: city_name (nombre de la ciudad)
    RETORNA: JSON con serie temporal generada
    """
    try:
        # Buscar ciudad
        selected_city = None
        for key, city in CITIES.items():
            if city['name'].lower() == city_name.lower():
                selected_city = city
                break
        
        if not selected_city:
            return jsonify({
                'success': False,
                'message': f'Ciudad "{city_name}" no encontrada'
            }), 404
        
        # Generar datos
        city_data = generate_airvisual_data(selected_city)
        
        if city_data is None:
            return jsonify({
                'success': False,
                'message': 'No se pudieron generar datos'
            }), 500
        
        # Convertir DataFrame a formato JSON-friendly
        data_dict = {
            'dates': city_data['date'].dt.strftime('%Y-%m-%d').tolist(),
            'pm25': city_data['PM2.5'].round(1).tolist(),
            'no2': city_data['NO2'].round(1).tolist()
        }
        
        return jsonify({
            'success': True,
            'city': selected_city['name'],
            'data': data_dict,
            'total_days': len(city_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generando datos: {str(e)}'
        }), 500

# ========================================
# INICIALIZACIÓN Y EJECUCIÓN
# ========================================

if __name__ == '__main__':
    print("🚀 Iniciando API de Predicción de Calidad del Aire...")
    
    # Inicializar modelo
    if initialize_model():
        print("✅ Modelo inicializado correctamente")
    else:
        print("⚠️ Modelo no inicializado, se entrenará cuando sea necesario")
    
    print("\n📍 ENDPOINTS DISPONIBLES:")
    print("GET  /api/health - Estado del servidor")
    print("GET  /api/cities - Lista de ciudades disponibles")
    print("GET  /api/cities/{city} - Datos actuales de una ciudad")
    print("POST /api/predict - Hacer predicción")
    print("POST /api/train - Entrenar modelo")
    print("GET  /api/generate-data/{city} - Generar serie temporal")
    
    print("\n🌐 Servidor ejecutándose en: http://localhost:5000")
    print("📱 Listo para conectar con React Frontend")
    
    # Ejecutar servidor Flask
    app.run(
        host='0.0.0.0',    # Permitir conexiones externas
        port=5000,         # Puerto 5000
        debug=True         # Modo desarrollo con recarga automática
    )