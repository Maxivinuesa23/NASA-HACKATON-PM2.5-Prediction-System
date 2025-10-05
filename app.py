from flask import Flask, jsonify, request
from flask_cors import CORS
import torch
import numpy as np
from datetime import datetime, timedelta
import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


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


app = Flask(__name__)
CORS(app)  

MODEL_PATH = 'air_quality_predictor_model.pth'
model = None  
cached_data = {}  

def initialize_model():
    """
    FUNCTION: Initializes and loads the LSTM model

    PURPOSE: Prepare model for making predictions
    """
    global model
    print("Initializing LSTM model...")
    
    try:
        model = AirQualityPredictor(N_FEATURES, HIDDEN_DIM, NUM_LAYERS, OUTPUT_DIM, DROPOUT_RATE)
        
        if os.path.exists(MODEL_PATH):
            model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
            print("Model loaded successfully")
        else:
            print("Model not found, it will be trained when needed")

        return True
    except Exception as e:
        print(f"Error initializing model: {e}")
        return False

def ensure_model_trained(city_data):
    """
    FUNCTION: Ensures the model is trained with city data
    PURPOSE: Train model if it does not exist or if necessary
    """
    global model
    
    if not os.path.exists(MODEL_PATH):
        print(" Training model with current data...")
        
        try:
            from torch.utils.data import DataLoader, random_split
            
            full_dataset = AirQualityDataset(city_data, SEQ_LENGTH)
            
            train_size = int(0.8 * len(full_dataset))
            val_size = len(full_dataset) - train_size
            train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
            
            train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
            
            train_model(model, train_loader, val_loader)
            
            torch.save(model.state_dict(), MODEL_PATH)
            print(" Model trained and saved")
            
        except Exception as e:
            print(f" Error training model: {e}")
            return False
    
    return True

def predict_next_day_pm25(city_info):
    """
    FUNCTION: Predicts PM2.5 for the next day
    PURPOSE: Use LSTM model to generate prediction
    """
    try:
        city_data = generate_airvisual_data(city_info)
        
        if city_data is None or len(city_data) < SEQ_LENGTH + 10:
            return None
            
        if not ensure_model_trained(city_data):
            return None
            
        full_dataset = AirQualityDataset(city_data, SEQ_LENGTH)
        last_sequence_data, _ = full_dataset[len(full_dataset)-1]
        prediction_sequence = last_sequence_data.cpu().numpy()
        
        predicted_pm25 = make_single_prediction(model, prediction_sequence)
        
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
            'confidence': 0.85  # Placeholder for confidence
        }
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None


# ENDPOINTS DE LA API

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    ENDPOINT: Server status
    RETURNS: JSON with system health status
    """
    return jsonify({
        'status': 'healthy',
        'message': 'API Air Quality Predictor working',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None,
        'device': str(DEVICE)
    })

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """
    ENDPOINT: List of available cities
    RETURNS: JSON with all cities that can be queried
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
    ENDPOINT: Current data for a specific city
    PARAMETER: city_name (name of the city)
    RETURNS: JSON with current data and prediction
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
            'temperature': round(np.random.normal(22, 8), 1),  
            'humidity': round(np.random.normal(60, 20), 1),    
            'wind_speed': round(np.random.normal(15, 5), 1),   
            'pressure': round(np.random.normal(1013, 20), 1)   
        }
        
        # Convertir PM2.5 a AQI para clasificación
        pm25_value = latest_data['PM2.5']
        aqi_approx = min(500, max(0, pm25_value * 2))  # Aproximación simple
        quality_level, quality_emoji = get_aqi_quality_level(aqi_approx)
        
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
    ENDPOINT: Specific prediction for a city
    METHOD: POST with JSON body {'city': 'city_name'}
    RETURNS: JSON with detailed prediction
    """
    try:
        data = request.get_json()
        
        if not data or 'city' not in data:
            return jsonify({
                'success': False,
                'message': 'The city is missing from the JSON.'
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
                'message': f'City "{city_name}" not found.'
            }), 404
        
        # Obtener predicción
        prediction = predict_next_day_pm25(selected_city)
        
        if not prediction:
            return jsonify({
                'success': False,
                'message': 'Failed to generate prediction.'
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
            'message': f'Error in prediction: {str(e)}'
        }), 500

@app.route('/api/train', methods=['POST'])
def train_model_endpoint():
    """
    ENDPOINT: Force re-training of the model
    METHOD: POST with JSON body {'city': 'city_name'}
    RETURNS: JSON with training result
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
                'message': 'No training data could be obtained'
            }), 500
        
        success = ensure_model_trained(city_data)
        
        return jsonify({
            'success': success,
            'message': 'Model re-trained successfully' if success else 'Error in training',
            'city': selected_city['name'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Training Error: {str(e)}'
        }), 500

@app.route('/api/generate-data/<city_name>', methods=['GET'])
def generate_city_data(city_name):
    """
    ENDPOINT: Generate new time series for a city
    PARAMETER: city_name (name of the city)
    RETURNS: JSON with generated time series
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
                'message': f'City "{city_name}" not found.'
            }), 404
        
        # Generar datos
        city_data = generate_airvisual_data(selected_city)
        
        if city_data is None:
            return jsonify({
                'success': False,
                'message': 'Failed to generate data'
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
            'message': f'Error to generate data: {str(e)}'
        }), 500

# ========================================
# INICIALIZACIÓN Y EJECUCIÓN
# ========================================

if __name__ == '__main__':
    print("Initializing API")
    
    # Inicializar modelo
    if initialize_model():
        print("API OK")
    else:
        print("API Initialization Failed")
    
    print("\n AVAILABLE ENDPOINTS:")
    print("GET  /api/health - Server status")
    print("GET  /api/cities - List of available cities")
    print("GET  /api/cities/{city} - Current data for a city")
    print("POST /api/predict - Make a prediction")
    print("POST /api/train - Train the model")
    print("GET  /api/generate-data/{city} - Generate time series")

    # Ejecutar servidor Flask
    app.run(
        host='0.0.0.0',    # Permitir conexiones externas
        port=5000,         # Puerto 5000
        debug=True         # Modo desarrollo con recarga automática
    )