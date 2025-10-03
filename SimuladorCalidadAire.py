import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler
import openaq
import requests
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE CIUDADES DISPONIBLES ---
CITIES = {
    "1": {
        "name": "Ciudad de México",
        "bbox": "-99.2,19.3,-99.0,19.5"  # Corregido: lat debe ser positiva
    },
    "2": {
        "name": "Nueva York",
        "bbox": "-74.0,40.7,-73.9,40.8"
    },
    "3": {
        "name": "Los Ángeles", 
        "bbox": "-118.5,33.9,-118.2,34.1"
    },
    "4": {
        "name": "Madrid",
        "bbox": "-3.8,40.3,-3.6,40.5"
    },
    "5": {
        "name": "Londres",
        "bbox": "-0.2,51.4,0.0,51.6"
    },
    "6": {
        "name": "Buenos Aires",
        "bbox": "-58.5,-34.7,-58.3,-34.5"
    }
}

def select_city():
    """
    Permite al usuario seleccionar una ciudad de la lista disponible.
    """
    print("\n🌍 CIUDADES DISPONIBLES:")
    print("-" * 30)
    for key, city in CITIES.items():
        print(f"{key}. {city['name']}")
    
    while True:
        try:
            choice = input("\n🏙️  Elige una ciudad (1-6): ").strip()
            if choice in CITIES:
                selected_city = CITIES[choice]
                print(f"✅ Has seleccionado: {selected_city['name']}")
                return selected_city
            else:
                print("❌ Opción no válida. Elige un número del 1 al 6.")
        except KeyboardInterrupt:
            print("\n⚠️  Operación cancelada. Usando Ciudad de México por defecto.")
            return CITIES["1"]

# --- CONFIGURACIÓN DE PARÁMETROS ---
SEQ_LENGTH = 10
N_FEATURES = 5

# Variables globales
SCALER = None 
today = datetime.now().date()
tomorrow = today + timedelta(days=1)

def get_api_key():
    """
    Obtiene la API key desde el archivo config.py
    """
    try:
        from config import OPENAQ_API_KEY
        return OPENAQ_API_KEY
    except ImportError:
        print("❌ No se encontró el archivo config.py")
        return None
    except AttributeError:
        print("❌ OPENAQ_API_KEY no está definida en config.py")
        return None

class AirQualityDataset(Dataset):
    """
    Dataset personalizado para datos de calidad del aire.
    """
    def __init__(self, data, seq_length):
        self.data = torch.FloatTensor(data)
        self.seq_length = seq_length
        
    def __len__(self):
        return len(self.data) - self.seq_length
    
    def __getitem__(self, idx):
        X = self.data[idx:idx+self.seq_length]
        y = self.data[idx+self.seq_length][1]
        return X, y

def get_openaq_parameter_data(parameter, bbox, limit=1000):
    """
    Obtiene datos de un parámetro específico desde la API v3 de OpenAQ.
    Usa el enfoque correcto: locations -> latest measurements
    """
    api_key = get_api_key()
    if not api_key or api_key == "TU_API_KEY_AQUI":
        return None
        
    headers = {'X-API-Key': api_key, 'Accept': 'application/json'}
    
    try:
        # Paso 1: Buscar ubicaciones en el área geográfica
        locations_url = "https://api.openaq.org/v3/locations"
        
        # Convertir bbox a parámetros individuales
        bbox_parts = bbox.split(',')
        if len(bbox_parts) == 4:
            params = {
                'limit': 50,
                'coordinates': f"{bbox_parts[1]},{bbox_parts[0]}",  # lat,lng
                'radius': 25000  # 25km radius
            }
        else:
            params = {'limit': 50}
        
        response = requests.get(locations_url, headers=headers, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"   ❌ Error buscando ubicaciones: {response.status_code}")
            return None
        
        data = response.json()
        locations = data.get('results', [])
        
        if not locations:
            print(f"   ❌ No se encontraron ubicaciones en el área")
            return None
        
        print(f"   🔍 Encontradas {len(locations)} ubicaciones")
        
        # Paso 2: Buscar ubicaciones con datos recientes
        all_values = []
        locations_with_data = 0
        
        for location in locations[:10]:  # Probar hasta 10 ubicaciones
            location_id = location['id']
            location_name = location.get('name', 'Unknown')
            
            # Verificar si tiene datos recientes
            if not location.get('datetimeLast'):
                continue
                
            # Obtener mediciones latest de esta ubicación
            latest_url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
            latest_response = requests.get(latest_url, headers=headers, timeout=10)
            
            if latest_response.status_code == 200:
                latest_data = latest_response.json()
                measurements = latest_data.get('results', [])
                
                # Buscar el parámetro específico o usar heurística
                for measurement in measurements:
                    param = measurement.get('parameter', {})
                    value = measurement.get('value')
                    
                    if value is not None and value >= 0:
                        # Si el parámetro está identificado correctamente
                        if param.get('id') == parameter:
                            all_values.append(value)
                            locations_with_data += 1
                            print(f"   ✅ {location_name}: {value} μg/m³ (parámetro {parameter})")
                            break
                        # Si no hay ID de parámetro, usar heurística basada en rango de valores
                        elif param.get('id') is None:
                            # PM2.5 (parameter 2): típicamente 0-500 μg/m³
                            # NO2 (parameter 3): típicamente 0-200 μg/m³
                            if parameter == 2 and 0 <= value <= 500:  # PM2.5
                                all_values.append(value)
                                locations_with_data += 1
                                print(f"   ✅ {location_name}: {value} μg/m³ (estimado PM2.5)")
                                break
                            elif parameter == 3 and 0 <= value <= 200:  # NO2
                                all_values.append(value)
                                locations_with_data += 1
                                print(f"   ✅ {location_name}: {value} μg/m³ (estimado NO2)")
                                break
        
        if all_values:
            print(f"   🎯 Total: {len(all_values)} mediciones de {locations_with_data} ubicaciones")
            return all_values
        else:
            print(f"   ❌ No se encontraron mediciones del parámetro {parameter}")
            return None
            
    except Exception as e:
        print(f"   ⚠️  Error en API v3: {e}")
        return None

def generate_openaq_data(city=None):
    """
    Genera datos de calidad del aire usando la API v3 de OpenAQ para la ciudad seleccionada.
    """
    global SCALER
    
    if city is None:
        city = CITIES["1"]
    
    print(f"\n🏙️  Obteniendo datos para: {city['name']}")
    
    # Intentar obtener datos reales
    pm25_data = get_openaq_parameter_data(2, city['bbox'])
    no2_data = get_openaq_parameter_data(3, city['bbox'])
    
    if not pm25_data and not no2_data:
        print(f"❌ No hay datos disponibles para {city['name']}")
        return None
    
    # Procesar datos reales disponibles con filtros más estrictos
    real_data = {}
    if pm25_data:
        # Filtrar valores extremos de PM2.5 - más estricto para evitar valores irreales
        pm25_filtered = [x for x in pm25_data if 0 <= x <= 100]  # Límite más estricto
        if pm25_filtered:
            real_data['pm25'] = pm25_filtered
            pm25_mean, pm25_std = np.mean(pm25_filtered), np.std(pm25_filtered)
            print(f"   ✅ PM2.5 real - Media: {pm25_mean:.2f}, Std: {pm25_std:.2f}")
            print(f"   📊 Rango PM2.5: {min(pm25_filtered):.1f} - {max(pm25_filtered):.1f} μg/m³")
            print(f"   🔍 Filtradas {len(pm25_data) - len(pm25_filtered)} mediciones extremas")
    
    if no2_data:
        # Filtrar valores extremos para NO2
        no2_filtered = [x for x in no2_data if 0 <= x <= 80]  # Filtro para NO2
        if no2_filtered:
            real_data['no2'] = no2_filtered
            no2_mean, no2_std = np.mean(no2_filtered), np.std(no2_filtered)
            print(f"   ✅ NO2 real - Media: {no2_mean:.2f}, Std: {no2_std:.2f}")
    
    if not real_data:
        print("❌ No hay datos válidos después del filtrado")
        return None
    
    # Generar serie temporal usando datos reales como base con valores más realistas
    n_days = SEQ_LENGTH + 50
    end_date = today
    start_date = end_date - timedelta(days=n_days-1)
    
    # Generar fechas
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Usar estadísticas reales para generar serie coherente
    np.random.seed(42)
    
    data_series = {}
    
    # PM2.5 basado en datos reales pero con límites más conservadores
    if 'pm25' in real_data:
        base_pm25 = min(50, np.mean(real_data['pm25']))  # Limitar base a 50
        std_pm25 = min(12, np.std(real_data['pm25']))    # Limitar variabilidad
        # Generar serie con tendencia realista
        trend = np.linspace(base_pm25 * 1.1, base_pm25 * 0.9, n_days)
        noise = np.random.normal(0, std_pm25 * 0.3, n_days)
        data_series['PM2.5'] = np.clip(trend + noise, 1, 80)  # Clip a valores razonables
    else:
        data_series['PM2.5'] = np.clip(np.random.gamma(2, 15), 5, 60)  # Valores típicos urbanos
    
    # NO2 basado en datos reales
    if 'no2' in real_data:
        base_no2 = min(35, np.mean(real_data['no2']))
        std_no2 = min(8, np.std(real_data['no2']))
        trend = np.linspace(base_no2 * 1.1, base_no2 * 0.9, n_days)
        noise = np.random.normal(0, std_no2 * 0.3, n_days)
        data_series['NO2'] = np.clip(trend + noise, 1, 60)
    else:
        data_series['NO2'] = np.clip(data_series['PM2.5'] * 0.6 + np.random.normal(0, 5, n_days), 1, 50)
    
    # Variables meteorológicas sintéticas pero realistas
    data_series['Wind_Speed'] = np.maximum(np.random.gamma(2, 2, n_days), 0.1)
    data_series['Humidity'] = np.clip(np.random.normal(60, 15, n_days), 10, 95)
    data_series['Temperature'] = 20 + 10 * np.sin(np.linspace(0, 4*np.pi, n_days)) + np.random.normal(0, 3, n_days)
    
    # Crear DataFrame
    final_df = pd.DataFrame(data_series, index=date_range)
    
    print(f"   ✅ Serie temporal generada con {len(final_df)} días")
    print(f"   📊 PM2.5 - Media: {final_df['PM2.5'].mean():.1f}, Rango: {final_df['PM2.5'].min():.1f}-{final_df['PM2.5'].max():.1f}")
    
    # Normalización
    feature_columns = ['PM2.5', 'NO2', 'Wind_Speed', 'Humidity', 'Temperature']
    data_to_scale = final_df[feature_columns].values
    
    SCALER = StandardScaler()
    scaled_data = SCALER.fit_transform(data_to_scale)
    
    print(f"   📊 Basado en {len(pm25_data) if pm25_data else 0} mediciones reales de PM2.5")
    
    return scaled_data

def generate_synthetic_data(city=None):
    """
    Genera datos sintéticos para cuando no hay datos reales disponibles.
    Personaliza los datos según la ciudad seleccionada.
    """
    global SCALER
    
    if city is None:
        city = CITIES["1"]  # Ciudad de México por defecto
    
    print(f"🔄 Generando datos sintéticos para {city['name']}...")
    
    N_SAMPLES = SEQ_LENGTH + 100
    
    # Configuración específica por ciudad
    city_profiles = {
        "Ciudad de México": {"pm25_base": 35, "pm25_std": 15, "no2_base": 25},
        "Nueva York": {"pm25_base": 20, "pm25_std": 8, "no2_base": 20},
        "Los Ángeles": {"pm25_base": 25, "pm25_std": 12, "no2_base": 22},
        "Madrid": {"pm25_base": 18, "pm25_std": 7, "no2_base": 18},
        "Londres": {"pm25_base": 15, "pm25_std": 6, "no2_base": 15},
        "Buenos Aires": {"pm25_base": 22, "pm25_std": 10, "no2_base": 19}
    }
    
    profile = city_profiles.get(city['name'], city_profiles["Nueva York"])
    
    # Generar datos sintéticos más realistas
    np.random.seed(42)
    
    # PM2.5: valores específicos por ciudad
    pm25_base = np.random.gamma(2, profile['pm25_base'] / 2, N_SAMPLES)
    pm25 = np.clip(pm25_base, 5, 80)
    
    # NO2: correlacionado con PM2.5 pero con su propia variabilidad
    no2 = pm25 * 0.7 + np.random.normal(0, 5, N_SAMPLES)
    no2 = np.clip(no2, 0, 60)
    
    # Variables meteorológicas
    wind_speed = np.random.exponential(3, N_SAMPLES)
    humidity = np.random.normal(55, 20, N_SAMPLES)
    humidity = np.clip(humidity, 10, 95)
    
    # Temperatura con variación estacional
    temp_base = 18 + 8 * np.sin(np.linspace(0, 4*np.pi, N_SAMPLES))
    temperature = temp_base + np.random.normal(0, 4, N_SAMPLES)
    
    # Combinar en array
    synthetic_data = np.column_stack([pm25, no2, wind_speed, humidity, temperature])
    
    # Normalizar
    SCALER = StandardScaler()
    scaled_data = SCALER.fit_transform(synthetic_data)
    
    print(f"   📊 {N_SAMPLES} días sintéticos generados para {city['name']}")
    print(f"   📊 PM2.5 - Media: {pm25.mean():.1f}, Rango: {pm25.min():.1f}-{pm25.max():.1f}")
    
    return scaled_data