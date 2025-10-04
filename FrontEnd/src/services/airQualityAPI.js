// Servicio para conectar con la API de calidad del aire
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Configurar axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejo de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const airQualityAPI = {
  // Verificar estado del servidor
  async getHealth() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Servidor no disponible');
    }
  },

  // Obtener lista de ciudades
  async getCities() {
    try {
      const response = await api.get('/cities');
      return response.data;
    } catch (error) {
      throw new Error('Error obteniendo ciudades');
    }
  },

  // Obtener datos de una ciudad específica
  async getCityData(cityName) {
    try {
      const response = await api.get(`/cities/${encodeURIComponent(cityName)}`);
      return response.data;
    } catch (error) {
      throw new Error(`Error obteniendo datos de ${cityName}`);
    }
  },

  // Hacer predicción específica
  async predict(cityName) {
    try {
      const response = await api.post('/predict', { city: cityName });
      return response.data;
    } catch (error) {
      throw new Error(`Error prediciendo para ${cityName}`);
    }
  }
};