// Servicio para conectar con la API de calidad del aire
// Versión con fallback para producción en Vercel

const API_BASE_URL = import.meta.env.PROD ? 
  'https://your-python-backend-url.com/api' : // Cambia esto por tu backend en producción
  'http://localhost:5000/api';

// Datos de fallback para demostración en producción
const FALLBACK_DATA = {
  cities: [
    { id: '1', name: 'Ciudad de México' },
    { id: '2', name: 'Nueva York' },
    { id: '3', name: 'Los Ángeles' },
    { id: '4', name: 'Madrid' },
    { id: '5', name: 'Londres' },
    { id: '6', name: 'Mendoza' },
    { id: '7', name: 'Aksu' }
  ],
  cityData: {
    'Ciudad de México': {
      current: {
        pm25: 38.7,
        aqi: 77,
        quality_level: 'MODERATE',
        weather: { temperature: 22, humidity: 55 }
      },
      prediction: {
        predicted_pm25: 42.1,
        tomorrow_pm25: 39.8,
        prediction_date: new Date().toISOString().split('T')[0],
        confidence: 0.87
      }
    },
    'Nueva York': {
      current: {
        pm25: 15.3,
        aqi: 45,
        quality_level: 'GOOD',
        weather: { temperature: 18, humidity: 62 }
      },
      prediction: {
        predicted_pm25: 18.7,
        tomorrow_pm25: 16.2,
        prediction_date: new Date().toISOString().split('T')[0],
        confidence: 0.82
      }
    },
    'Los Ángeles': {
      current: {
        pm25: 45.2,
        aqi: 89,
        quality_level: 'UNHEALTHY FOR SENSITIVE',
        weather: { temperature: 24, humidity: 48 }
      },
      prediction: {
        predicted_pm25: 49.8,
        tomorrow_pm25: 52.1,
        prediction_date: new Date().toISOString().split('T')[0],
        confidence: 0.85
      }
    },
    'Madrid': {
      current: {
        pm25: 32.1,
        aqi: 72,
        quality_level: 'MODERATE',
        weather: { temperature: 16, humidity: 58 }
      },
      prediction: {
        predicted_pm25: 28.6,
        tomorrow_pm25: 31.4,
        prediction_date: new Date().toISOString().split('T')[0],
        confidence: 0.79
      }
    },
    'Londres': {
      current: {
        pm25: 28.9,
        aqi: 68,
        quality_level: 'MODERATE',
        weather: { temperature: 14, humidity: 71 }
      },
      prediction: {
        predicted_pm25: 25.2,
        tomorrow_pm25: 27.8,
        prediction_date: new Date().toISOString().split('T')[0],
        confidence: 0.83
      }
    },
    'Mendoza': {
      current: {
        pm25: 8.4,
        aqi: 28,
        quality_level: 'GOOD',
        weather: { temperature: 19, humidity: 45 }
      },
      prediction: {
        predicted_pm25: 10.8,
        tomorrow_pm25: 9.2,
        prediction_date: new Date().toISOString().split('T')[0],
        confidence: 0.88
      }
    },
    'Aksu': {
      current: {
        pm25: 167.3,
        aqi: 225,
        quality_level: 'HAZARDOUS',
        weather: { temperature: 26, humidity: 35 }
      },
      prediction: {
        predicted_pm25: 159.7,
        tomorrow_pm25: 174.2,
        prediction_date: new Date().toISOString().split('T')[0],
        confidence: 0.76
      }
    }
  }
};

// Función para simular delay de red
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const airQualityAPI = {
  // Verificar estado del servidor
  async getHealth() {
    await delay(500); // Simular latencia
    
    if (import.meta.env.PROD) {
      // En producción, usar datos simulados
      return {
        status: 'healthy',
        message: 'Demo mode - using simulated data',
        mode: 'production'
      };
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error('Network error');
      return await response.json();
    } catch (error) {
      console.warn('Backend not available, using fallback data');
      return {
        status: 'healthy',
        message: 'Using fallback data',
        mode: 'fallback'
      };
    }
  },

  // Obtener lista de ciudades
  async getCities() {
    await delay(300);
    
    if (import.meta.env.PROD) {
      return {
        success: true,
        cities: FALLBACK_DATA.cities,
        message: 'Demo data loaded'
      };
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/cities`);
      if (!response.ok) throw new Error('Network error');
      return await response.json();
    } catch (error) {
      console.warn('Backend not available, using fallback cities');
      return {
        success: true,
        cities: FALLBACK_DATA.cities,
        message: 'Fallback cities loaded'
      };
    }
  },

  // Obtener datos de una ciudad específica
  async getCityData(cityName) {
    await delay(800);
    
    if (import.meta.env.PROD) {
      const cityData = FALLBACK_DATA.cityData[cityName];
      if (cityData) {
        return {
          success: true,
          data: cityData,
          message: `Demo data for ${cityName}`
        };
      } else {
        throw new Error(`No demo data available for ${cityName}`);
      }
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/cities/${encodeURIComponent(cityName)}`);
      if (!response.ok) throw new Error('Network error');
      return await response.json();
    } catch (error) {
      console.warn(`Backend not available for ${cityName}, using fallback data`);
      const cityData = FALLBACK_DATA.cityData[cityName];
      if (cityData) {
        return {
          success: true,
          data: cityData,
          message: `Fallback data for ${cityName}`
        };
      } else {
        throw new Error(`No fallback data available for ${cityName}`);
      }
    }
  },

  // Hacer predicción específica
  async predict(cityName) {
    await delay(1000);
    
    if (import.meta.env.PROD) {
      const cityData = FALLBACK_DATA.cityData[cityName];
      if (cityData) {
        return {
          success: true,
          prediction: cityData.prediction,
          message: `Demo prediction for ${cityName}`
        };
      }
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city: cityName })
      });
      if (!response.ok) throw new Error('Network error');
      return await response.json();
    } catch (error) {
      console.warn(`Prediction backend not available for ${cityName}, using fallback`);
      const cityData = FALLBACK_DATA.cityData[cityName];
      if (cityData) {
        return {
          success: true,
          prediction: cityData.prediction,
          message: `Fallback prediction for ${cityName}`
        };
      } else {
        throw new Error(`No fallback prediction for ${cityName}`);
      }
    }
  }
};