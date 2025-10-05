# Configuración de API Keys
# API de AirVisual (IQAir)
import os

# API Key de AirVisual
# Obtén tu API key en: https://www.iqair.com/air-quality-monitors/api
# Configura la variable de entorno AIRVISUAL_API_KEY
AIRVISUAL_API_KEY = os.getenv("AIRVISUAL_API_KEY")
AIRVISUAL_BASE_URL = "http://api.airvisual.com/v2/"