# ========================================
# SIMULADOR DE CALIDAD DEL AIRE CON AIRVISUAL API
# Sistema completo para obtener y procesar datos de calidad del aire
# ========================================

# IMPORTACIONES: Librerías necesarias para el funcionamiento
import numpy as np                      # Para operaciones matemáticas y arrays numéricos
import pandas as pd                     # Para manejo de datos tabulares (tablas/DataFrames)
import torch                           # Framework de machine learning PyTorch
from torch.utils.data import Dataset   # Clase base para crear datasets personalizados
from sklearn.preprocessing import StandardScaler  # Para normalizar datos (escalar entre 0 y 1)
import requests                        # Para hacer peticiones HTTP a APIs externas
from datetime import datetime, timedelta  # Para manejo y cálculo de fechas
import time                           # Para pausas y esperas en el código

# ========================================
# CONFIGURACIÓN DE CIUDADES DISPONIBLES
# Diccionario con información de cada ciudad para la API
# ========================================
CITIES = {
    "1": {                              # Opción 1 para el usuario
        "name": "Ciudad de México",      # Nombre amigable para mostrar
        "city": "Mexico City",           # Nombre exacto que requiere AirVisual API
        "state": "Mexico City",          # Estado/provincia para la API
        "country": "Mexico"              # País en inglés para la API
    },
    "2": {                              # Opción 2 para el usuario
        "name": "Nueva York",           # Nombre amigable para mostrar
        "city": "New York City",        # Nombre exacto que requiere AirVisual API
        "state": "New York",            # Estado de Nueva York
        "country": "USA"                # Estados Unidos
    },
    "3": {                              # Opción 3 para el usuario
        "name": "Los Ángeles",          # Nombre amigable para mostrar
        "city": "Los Angeles",          # Nombre exacto para la API
        "state": "California",          # Estado de California
        "country": "USA"                # Estados Unidos
    },
    "4": {                              # Opción 4 para el usuario
        "name": "Madrid",               # Nombre amigable para mostrar
        "city": "Madrid",               # Nombre exacto para la API
        "state": "Madrid",              # Comunidad de Madrid
        "country": "Spain"              # España
    },
    "5": {                              # Opción 5 para el usuario
        "name": "Londres",              # Nombre amigable para mostrar
        "city": "London",               # Nombre en inglés para la API
        "state": "England",             # Inglaterra como estado
        "country": "UK"                 # Reino Unido
    },
    "6": {                              # Opción 6 para el usuario
        "name": "Mendoza, Argentina",   # Nombre amigable (única ciudad argentina disponible)
        "city": "Mendoza",              # Nombre exacto para la API
        "state": "Mendoza",             # Provincia de Mendoza
        "country": "Argentina"          # Argentina
    },
    "7":{
        "name": "Aksu",              # Nombre amigable (única ciudad china disponible)
        "city": "Aksu",              # Nombre exacto para la API
        "state": "Xinjiang",         # Región de Xinjiang
        "country": "China"           # China
    }

    #Aksu

}

# ========================================
# CONFIGURACIÓN GLOBAL DEL SISTEMA
# Parámetros que usa todo el programa
# ========================================
SEQ_LENGTH = 10                        # Días de historial que usa el modelo para predecir (ventana temporal)
N_FEATURES = 2                         # Número de variables que predecimos (PM2.5 y NO2)
SCALER = StandardScaler()              # Objeto global para normalizar datos (convierte a escala 0-1)

def aqi_to_pm25(aqi_us):
    """
    FUNCIÓN: Convierte AQI US a concentración de PM2.5 en μg/m³
    PROPÓSITO: La API devuelve AQI, pero necesitamos PM2.5 real para entrenar
    FÓRMULA: Oficial de la EPA (Agencia de Protección Ambiental de EE.UU.)
    """
    if aqi_us <= 50:                   # Rango 1: AQI 0-50 = Aire BUENO
        return (aqi_us / 50) * 12.0    # Conversión lineal a 0-12 μg/m³
    elif aqi_us <= 100:                # Rango 2: AQI 51-100 = Aire MODERADO
        return 12.1 + ((aqi_us - 51) / 49) * (35.4 - 12.1)  # Fórmula EPA oficial
    elif aqi_us <= 150:                # Rango 3: AQI 101-150 = DAÑINO para grupos sensibles
        return 35.5 + ((aqi_us - 101) / 49) * (55.4 - 35.5)
    elif aqi_us <= 200:                # Rango 4: AQI 151-200 = DAÑINO para todos
        return 55.5 + ((aqi_us - 151) / 49) * (150.4 - 55.5)
    elif aqi_us <= 300:                # Rango 5: AQI 201-300 = MUY DAÑINO
        return 150.5 + ((aqi_us - 201) / 99) * (250.4 - 150.5)
    else:                              # Rango 6: AQI 301+ = PELIGROSO
        return 250.5 + (aqi_us - 301) * 1.5

def get_aqi_quality_level(aqi):
    """
    FUNCIÓN: Determina qué tan bueno o malo está el aire
    PROPÓSITO: Clasificar el AQI en categorías comprensibles para el usuario
    ENTRADA: Número AQI (0-500+)
    SALIDA: Texto descriptivo + emoji para mostrar al usuario
    """
    if aqi <= 50:                      # AQI 0-50: Lo mejor posible
        return "BUENA", "🟢"           # Verde = todo bien
    elif aqi <= 100:                   # AQI 51-100: Aceptable para la mayoría
        return "MODERADA", "🟡"        # Amarillo = precaución
    elif aqi <= 150:                   # AQI 101-150: Problemas para sensibles
        return "NO SALUDABLE (GRUPOS SENSIBLES)", "🟠"  # Naranja = cuidado
    elif aqi <= 200:                   # AQI 151-200: Malo para todos
        return "NO SALUDABLE", "🔴"    # Rojo = peligro
    elif aqi <= 300:                   # AQI 201-300: Muy malo
        return "MUY NO SALUDABLE", "🟣"  # Morado = emergencia
    else:                              # AQI 301+: Extremo
        return "PELIGROSA", "🔴"       # Rojo intenso = evacuación

def get_api_key():
    """
    FUNCIÓN: Obtiene la clave secreta de la API desde config.py
    PROPÓSITO: Mantener la API key segura y separada del código principal
    SEGURIDAD: config.py no se sube a GitHub (está en .gitignore)
    """
    try:                               # Intenta hacer algo que puede fallar
        from config import AIRVISUAL_API_KEY  # Importa la clave desde config.py
        return AIRVISUAL_API_KEY       # Si todo va bien, devuelve la clave
    except ImportError:                # Error: no encuentra el archivo config.py
        print("❌ No se encontró el archivo config.py")
        return None                    # Devuelve "nada" para indicar error
    except AttributeError:             # Error: config.py existe pero no tiene la variable
        print("❌ No se encontró AIRVISUAL_API_KEY en config.py")
        return None                    # Devuelve "nada" para indicar error

def get_airvisual_data(city_info, max_retries=3):
    """
    FUNCIÓN: Conecta con AirVisual API para obtener datos reales de calidad del aire
    PROPÓSITO: Obtener información actual de contaminación de una ciudad específica
    PARÁMETROS: city_info (diccionario con ciudad), max_retries (intentos máximos)
    RETORNA: Datos JSON de la API o None si falla
    """
    api_key = get_api_key()            # Obtiene la clave de API desde config.py
    if not api_key:                    # Si no hay clave disponible
        return None                    # Sale de la función sin hacer nada
    
    from config import AIRVISUAL_BASE_URL  # Importa la URL base desde config.py
    
    url = f"{AIRVISUAL_BASE_URL}city"  # Construye la URL completa para consulta de ciudad
    params = {                         # Parámetros que necesita la API
        'city': city_info['city'],     # Nombre de la ciudad en inglés
        'state': city_info['state'],   # Estado/provincia 
        'country': city_info['country'], # País en inglés
        'key': api_key                 # Clave de autenticación
    }
    
    print(f"   🌍 Consultando AirVisual API para {city_info.get('name', city_info['city'])}...")
    
    for attempt in range(max_retries):  # Reintenta hasta 3 veces si algo falla
        try:                           # Intenta hacer la petición HTTP
            response = requests.get(url, params=params, timeout=10)  # GET con timeout de 10 segundos
            
            if response.status_code == 200:    # Código 200 = éxito
                data = response.json()         # Convierte respuesta JSON a diccionario Python
                if data['status'] == 'success': # Verifica que la API diga "éxito"
                    return data['data']        # Devuelve solo la parte de datos útiles
                else:                          # API responde pero con error
                    print(f"   ⚠️  Error en API: {data.get('data', {}).get('message', 'Unknown error')}")
                    return None                # Termina la función
                    
            elif response.status_code == 429:  # Código 429 = demasiadas peticiones
                print(f"   ⏳ Rate limit alcanzado, esperando... (intento {attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)       # Espera exponencial: 2, 4, 8 segundos
                continue                       # Va al siguiente intento
                
            else:                             # Cualquier otro código de error
                print(f"   ❌ Error HTTP {response.status_code}")
                return None                   # Termina la función
                
        except requests.exceptions.RequestException as e:  # Error de conexión/red
            print(f"   ❌ Error de conexión (intento {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:     # Si no es el último intento
                time.sleep(1)                 # Espera 1 segundo
                continue                      # Va al siguiente intento
                
    return None                               # Si todos los intentos fallaron, devuelve None

def process_real_airvisual_data(real_data, city):
    """
    FUNCIÓN: Procesa y extrae información útil de la respuesta de AirVisual API
    PROPÓSITO: Convertir datos crudos de API en información comprensible
    ENTRADA: real_data (JSON de API), city (información de ciudad)
    SALIDA: DataFrame con serie temporal de 60 días
    """
    current = real_data.get('current', {})          # Extrae datos actuales del JSON
    pollution = current.get('pollution', {})        # Extrae datos de contaminación
    weather = current.get('weather', {})            # Extrae datos meteorológicos
    
    # EXTRACCIÓN DE DATOS PRINCIPALES
    aqi_us = pollution.get('aqius', 50)            # AQI estadounidense (default 50 si no hay)
    main_pollutant = pollution.get('mainus', 'unknown')  # Contaminante principal (pm25, no2, etc)
    temp = weather.get('tp', 20)                   # Temperatura en °C (default 20)
    humidity = weather.get('hu', 50)               # Humedad relativa % (default 50)
    
    # CONVERSIÓN CRÍTICA: AQI → PM2.5
    pm25_converted = aqi_to_pm25(aqi_us)           # Usa fórmula EPA para convertir
    
    # MOSTRAR RESULTADOS AL USUARIO
    print(f"   ✅ Datos obtenidos exitosamente!")
    print(f"   📊 AQI US: {aqi_us} (contaminante principal: {main_pollutant})")
    print(f"   🧮 PM2.5 convertido: {pm25_converted:.1f} μg/m³")  # .1f = 1 decimal
    
    # CLASIFICACIÓN DE CALIDAD DEL AIRE
    quality_level, quality_emoji = get_aqi_quality_level(aqi_us)  # Obtiene clasificación
    print(f"   {quality_emoji} Calidad del aire: {quality_level}")
    print(f"   🌡️  Temperatura: {temp}°C, Humedad: {humidity}%")
    
    # GENERAR HISTÓRICO BASADO EN DATOS REALES
    return generate_time_series_from_real_data(city, pm25_converted)  # Crea 60 días de datos

def generate_time_series_from_real_data(city, base_pm25):
    """
    FUNCIÓN: Crea 60 días de datos históricos basados en el valor real actual
    PROPÓSITO: El modelo necesita historial para entrenar, pero solo tenemos 1 dato actual
    MÉTODO: Genera variaciones realistas alrededor del valor real
    """
    n_days = SEQ_LENGTH + 50           # 10 (para modelo) + 50 (para entrenamiento) = 60 días
    today = datetime.now().date()      # Fecha de hoy
    end_date = today                  # La serie termina hoy
    start_date = end_date - timedelta(days=n_days-1)  # Comienza 60 días atrás
    
    # CREAR LISTA DE FECHAS
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')  # Fechas diarias
    
    # GENERAR SEMILLA ÚNICA POR CIUDAD (para consistencia)
    city_seed = hash(city['name']) % 1000  # Convierte nombre en número (0-999)
    np.random.seed(city_seed)              # Establece semilla para números aleatorios
    
    # GENERAR VARIACIONES REALISTAS DE PM2.5
    pm25_std = max(3, base_pm25 * 0.2)     # Desviación mínima 3, máxima 20% del valor base
    trend = np.linspace(base_pm25 * 1.1, base_pm25 * 0.9, n_days)  # Tendencia gradual descendente
    seasonal_variation = 5 * np.sin(2 * np.pi * np.arange(n_days) / 7)  # Patrón semanal
    noise = np.random.normal(0, pm25_std * 0.3, n_days)  # Ruido aleatorio diario
    pm25_series = np.clip(trend + seasonal_variation + noise, 5, 150)  # Combina todo, límites 5-150
    
    # GENERAR NO2 CORRELACIONADO CON PM2.5
    no2_base = min(60, max(10, base_pm25 * 0.6 + 15))  # NO2 base entre 10-60, correlacionado
    no2_trend = np.linspace(no2_base * 1.1, no2_base * 0.9, n_days)  # Tendencia similar
    no2_noise = np.random.normal(0, no2_base * 0.15, n_days)  # Ruido proporcional
    no2_series = np.clip(no2_trend + no2_noise, 5, 80)  # NO2 entre 5-80
    
    # CREAR TABLA DE DATOS (DataFrame)
    data = pd.DataFrame({               # Crea tabla con 3 columnas
        'date': date_range,            # Columna 1: fechas diarias
        'PM2.5': pm25_series,          # Columna 2: valores de PM2.5 generados
        'NO2': no2_series              # Columna 3: valores de NO2 generados
    })
    
    # MOSTRAR ESTADÍSTICAS AL USUARIO
    print(f"   ✅ Serie temporal generada con {len(data)} días")
    print(f"   📊 PM2.5 - Media: {np.mean(pm25_series):.1f}, Rango: {np.min(pm25_series):.1f}-{np.max(pm25_series):.1f}")
    print(f"   📊 NO2 - Media: {np.mean(no2_series):.1f}, Rango: {np.min(no2_series):.1f}-{np.max(no2_series):.1f}")
    print(f"   📊 Basado en datos reales de AirVisual API")
    
    return data                        # Devuelve la tabla con todos los datos generados

def generate_city_specific_synthetic_data(city):
    """
    FUNCIÓN: Genera datos sintéticos (falsos pero realistas) para ciudades sin datos reales
    PROPÓSITO: Simular patrones de contaminación específicos por ciudad
    MÉTODO: Usa perfiles predefinidos basados en características de cada ciudad
    """
    print(f"   🎯 Generando perfil sintético para {city['name']}")
    
    # PERFILES ESPECÍFICOS POR CIUDAD (basados en datos históricos reales)
    city_profiles = {
        "Ciudad de México": {"pm25_base": 35, "pm25_std": 12, "no2_base": 45, "no2_std": 8},  # Muy contaminada
        "Nueva York": {"pm25_base": 20, "pm25_std": 8, "no2_base": 30, "no2_std": 6},         # Moderada
        "Los Ángeles": {"pm25_base": 28, "pm25_std": 10, "no2_base": 38, "no2_std": 7},       # Alta por tráfico
        "Madrid": {"pm25_base": 18, "pm25_std": 7, "no2_base": 28, "no2_std": 5},             # Europea regulada
        "Londres": {"pm25_base": 15, "pm25_std": 6, "no2_base": 25, "no2_std": 4},            # Muy regulada
        "Mendoza, Argentina": {"pm25_base": 22, "pm25_std": 8, "no2_base": 28, "no2_std": 5}  # Región vinícola
    }
    
    # OBTENER PERFIL DE LA CIUDAD (o usar perfil genérico)
    profile = city_profiles.get(city['name'], {"pm25_base": 25, "pm25_std": 10, "no2_base": 30, "no2_std": 6})
    
    # CONFIGURAR PERIODO DE TIEMPO
    n_days = SEQ_LENGTH + 50           # 60 días total
    today = datetime.now().date()      # Fecha actual
    end_date = today                  # Termina hoy
    start_date = end_date - timedelta(days=n_days-1)  # Comienza 60 días atrás
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')  # Lista de fechas
    
    # GENERAR SEMILLA ESPECÍFICA POR CIUDAD (para consistencia entre ejecuciones)
    city_seed = hash(city['name']) % 1000  # Cada ciudad tiene su semilla única
    np.random.seed(city_seed)              # Fija la semilla
    
    # GENERAR PM2.5 CON PERFIL ESPECÍFICO
    pm25_base = profile['pm25_base']       # Valor base del perfil de la ciudad
    pm25_trend = np.linspace(pm25_base * 1.1, pm25_base * 0.9, n_days)  # Tendencia descendente
    pm25_seasonal = profile['pm25_std'] * 0.5 * np.sin(2 * np.pi * np.arange(n_days) / 30)  # Variación mensual
    pm25_noise = np.random.normal(0, profile['pm25_std'] * 0.3, n_days)  # Ruido diario
    pm25_series = np.clip(pm25_trend + pm25_seasonal + pm25_noise, 5, 100)  # Límites realistas
    
    # GENERAR NO2 CON PERFIL ESPECÍFICO
    no2_base = profile['no2_base']         # Valor base del perfil
    no2_trend = np.linspace(no2_base * 1.1, no2_base * 0.9, n_days)  # Tendencia similar
    no2_noise = np.random.normal(0, profile['no2_std'] * 0.4, n_days)  # Ruido proporcional
    no2_series = np.clip(no2_trend + no2_noise, 5, 80)  # Límites realistas para NO2
    
    # CREAR TABLA DE DATOS
    data = pd.DataFrame({
        'date': date_range,            # Fechas
        'PM2.5': pm25_series,          # PM2.5 sintético
        'NO2': no2_series              # NO2 sintético
    })
    
    # MOSTRAR ESTADÍSTICAS
    print(f"   ✅ Datos sintéticos específicos generados")
    print(f"   📊 PM2.5 - Media: {np.mean(pm25_series):.1f}, Rango: {np.min(pm25_series):.1f}-{np.max(pm25_series):.1f}")
    print(f"   📊 NO2 - Media: {np.mean(no2_series):.1f}, Rango: {np.min(no2_series):.1f}-{np.max(no2_series):.1f}")
    
    return data                        # Devuelve la tabla generada

def generate_airvisual_data(city=None):
    """
    FUNCIÓN PRINCIPAL: Coordinadora que obtiene datos reales o genera sintéticos
    PROPÓSITO: Punto de entrada único para obtener datos de cualquier ciudad
    ESTRATEGIA: 1° Intenta datos reales, 2° Genera sintéticos si falla
    """
    if city is None:                   # Si no se especifica ciudad
        city = CITIES["1"]             # Usa Ciudad de México por defecto
    
    print(f"\n🏙️  Obteniendo datos para: {city['name']}")
    
    # PASO 1: INTENTAR OBTENER DATOS REALES
    real_data = get_airvisual_data(city)  # Llama a la API de AirVisual
    
    if not real_data:                  # Si la API falla o no hay datos
        print(f"   ⚠️  No hay datos disponibles para {city['name']} en AirVisual API")
        print(f"   🎯 Generando datos sintéticos específicos para {city['name']}...")
        return generate_city_specific_synthetic_data(city)  # Genera datos falsos pero realistas
    
    # PASO 2: SI HAY DATOS REALES, PROCESARLOS
    return process_real_airvisual_data(real_data, city)  # Procesa datos reales

class AirQualityDataset(Dataset):
    """
    CLASE: Dataset personalizado para entrenar el modelo de machine learning
    PROPÓSITO: Convierte DataFrame en formato que entiende PyTorch
    HERENCIA: Extiende Dataset de PyTorch para funcionalidad ML
    """
    def __init__(self, data, seq_length=10):
        """
        CONSTRUCTOR: Inicializa el dataset cuando se crea el objeto
        PARÁMETROS: data (DataFrame), seq_length (días de historial)
        """
        self.seq_length = seq_length   # Guarda cuántos días de historial usar
        
        # PREPARAR DATOS NUMÉRICOS PARA EL MODELO
        numeric_data = data[['PM2.5', 'NO2']].values  # Extrae solo columnas numéricas como array
        
        # NORMALIZAR DATOS (convertir a escala 0-1)
        global SCALER                  # Usa el objeto global SCALER
        self.data = SCALER.fit_transform(numeric_data)  # Normaliza y guarda
        
        # VERIFICAR QUE HAY SUFICIENTES DATOS
        if len(self.data) < seq_length + 1:  # Necesita historial + 1 día para predecir
            raise ValueError(f"Necesitamos al menos {seq_length + 1} días de datos")
    
    def __len__(self):
        """
        MÉTODO: Dice cuántos ejemplos de entrenamiento hay
        RETORNA: Número de secuencias disponibles para entrenar
        """
        return len(self.data) - self.seq_length  # Total - historial = ejemplos disponibles
    
    def __getitem__(self, idx):
        """
        MÉTODO: Obtiene un ejemplo específico para entrenar
        PARÁMETRO: idx (índice del ejemplo que se quiere)
        RETORNA: X (historial), y (valor a predecir)
        """
        X = self.data[idx:idx+self.seq_length]     # Historial de seq_length días
        y = self.data[idx+self.seq_length][0]      # PM2.5 del día siguiente (columna 0)
        return torch.FloatTensor(X), torch.FloatTensor([y])  # Convierte a tensores de PyTorch

def select_city():
    """
    FUNCIÓN: Permite al usuario seleccionar una ciudad del menú
    PROPÓSITO: Interfaz de usuario para elegir qué ciudad analizar
    RETORNA: Diccionario con información de la ciudad seleccionada
    """
    print("\n🌍 CIUDADES DISPONIBLES:")
    print("-" * 30)
    for key, city in CITIES.items():   # Recorre todas las ciudades disponibles
        print(f"{key}. {city['name']}") # Muestra: "1. Ciudad de México"
    
    while True:                        # Bucle infinito hasta que el usuario elija bien
        try:                          # Intenta leer la entrada del usuario
            choice = input(f"\n🏙️  Elige una ciudad (1-{len(CITIES)}): ").strip()  # Pide selección
            if choice in CITIES:       # Si la opción existe en el diccionario
                selected_city = CITIES[choice]  # Obtiene la información completa
                print(f"✅ Has seleccionado: {selected_city['name']}")
                return selected_city   # Devuelve la ciudad seleccionada
            else:                     # Si la opción no es válida
                print(f"❌ Opción inválida. Elige entre 1 y {len(CITIES)}")
        except KeyboardInterrupt:     # Si el usuario presiona Ctrl+C
            print("\n👋 ¡Hasta luego!")
            exit()                    # Termina el programa
        except Exception as e:        # Cualquier otro error
            print(f"❌ Error: {e}")