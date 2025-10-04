import React, { useState, useEffect } from "react";
import { TrendingUp, Activity, Users, Zap } from "lucide-react";
import cloudbustersLogo from "./assets/cloudbusters.jpeg";
import AtmosphereEffect from "./AtmosphereEffect";
import MetricCard from "./MetricCard";
import Navbar from "./Navbar";
import { airQualityAPI } from "./services/airQualityAPI";

const App = () => {
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState('Conectando');
  const [airQualityData, setAirQualityData] = useState(null);
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('Ciudad de México');
  const [loadingCityData, setLoadingCityData] = useState(false);

  // Función para cargar datos de una ciudad específica
  const loadCityData = async (cityName) => {
    setLoadingCityData(true);
    try {
      const cityData = await airQualityAPI.getCityData(cityName);
      if (cityData.success) {
        setAirQualityData(cityData.data);
      } else {
        console.error('Error cargando datos de ciudad:', cityData.message);
      }
    } catch (error) {
      console.error('Error cargando datos de ciudad:', error);
    } finally {
      setLoadingCityData(false);
    }
  };

  // Función para verificar el estado del backend
  const checkBackendStatus = async () => {
    try {
      const health = await airQualityAPI.getHealth();
      if (health.status === 'healthy') {
        setBackendStatus('Funcionando');
        
        // Cargar ciudades
        const citiesData = await airQualityAPI.getCities();
        if (citiesData.success) {
          setCities(citiesData.cities);
          
          // Cargar datos de la ciudad seleccionada
          await loadCityData(selectedCity);
        }
      }
    } catch (error) {
      console.error('Error conectando con backend:', error);
      setBackendStatus('Desconectado');
    }
  };

  // Manejar cambio de ciudad
  const handleCityChange = async (cityName) => {
    setSelectedCity(cityName);
    await loadCityData(cityName);
  };

  // Simulación de carga para un efecto de fade-in
  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 500);
    checkBackendStatus();
    return () => clearTimeout(timer);
  }, []);

  // Datos de ejemplo para las tarjetas de métricas (ahora con datos reales si están disponibles)
  const metrics = [
    {
      title: "Calidad del Aire",
      value: airQualityData?.current?.pm25 || 42,
      unit: " PM2.5",
      icon: Activity,
      change: -5.2,
    },
    {
      title: "Predicción IA",
      value: airQualityData?.prediction?.predicted_pm25 || 38,
      unit: " PM2.5",
      icon: Zap,
      change: 2.1,
    },
    {
      title: "Ciudades Monitoreadas",
      value: cities.length || 7,
      unit: "",
      icon: Users,
      change: 0,
    },
    {
      title: "Temperatura",
      value: airQualityData?.current?.weather?.temperature || 22,
      unit: "°C",
      icon: TrendingUp,
      change: 1.5,
    },
  ];

  return (
    <div className={`min-h-screen font-sans relative overflow-hidden bg-gray-950 pt-16`}>
      {/* Configuración de fuentes */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
        body {
          font-family: 'Inter', sans-serif;
          margin: 0;
          padding: 0;
          overflow-x: hidden;
        }
      `}</style>

      {/* Barra de Navegación */}
      <Navbar />

      {/* Efecto Atmosférico */}
      <AtmosphereEffect />

      {/* Contenedor Principal */}
      <div className={`max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 transition-opacity duration-1000 ${
          loading ? "opacity-0" : "opacity-100"
        } relative z-20`}>
        
        {/* Encabezado con Logo */}
        <header className="mb-12 flex flex-col items-center text-center mt-8">
          <div className="w-48 h-48 mb-6 rounded-full overflow-hidden border-4 border-cyan-500/50 shadow-2xl shadow-cyan-500/30">
            <img
              src={cloudbustersLogo}
              alt="Cloudbusters Logo"
              className="w-full h-full object-cover mx-auto rounded-lg shadow-lg hover:scale-105 transition-transform duration-300"
            />
          </div>
          <h1 className="text-5xl font-extrabold text-white tracking-tight sm:text-6xl">
            Monitoreo{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-500">
              Atmosférico
            </span>
          </h1>
          <p className="mt-4 text-xl text-gray-400 max-w-3xl">
            Sistema de predicción de calidad del aire con inteligencia artificial.
          </p>
        </header>

        {/* Grid de Métricas con datos reales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {metrics.map((metric, index) => (
            <MetricCard key={index} {...metric} />
          ))}
        </div>

        {/* Estado del Sistema */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-white mb-6 text-center">
            Sistema de Monitoreo Integrado
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Frontend Status */}
            <div className="relative bg-gray-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-green-700/50">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-green-400 uppercase tracking-widest">
                  Frontend React
                </h3>
                <Activity className="w-5 h-5 text-green-400" />
              </div>
              <div className="text-2xl font-extrabold text-white mb-2">
                ✅ Funcionando
              </div>
              <div className="text-sm text-gray-400">
                Interfaz cargada correctamente
              </div>
            </div>

            {/* Backend Status */}
            <div className={`relative bg-gray-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border ${
              backendStatus === 'Funcionando' ? 'border-green-700/50' : 
              backendStatus === 'Conectando' ? 'border-yellow-700/50' : 'border-red-700/50'
            }`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className={`text-sm font-medium uppercase tracking-widest ${
                  backendStatus === 'Funcionando' ? 'text-green-400' : 
                  backendStatus === 'Conectando' ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  Backend Flask
                </h3>
                <Activity className={`w-5 h-5 ${
                  backendStatus === 'Funcionando' ? 'text-green-400' : 
                  backendStatus === 'Conectando' ? 'text-yellow-400' : 'text-red-400'
                }`} />
              </div>
              <div className="text-2xl font-extrabold text-white mb-2">
                {backendStatus === 'Funcionando' ? '✅' : 
                 backendStatus === 'Conectando' ? '🔄' : '❌'} {backendStatus}
              </div>
              <div className="text-sm text-gray-400">
                {backendStatus === 'Funcionando' ? 'API de IA operativa' : 
                 backendStatus === 'Conectando' ? 'API de IA preparándose' : 'API no disponible'}
              </div>
            </div>

            {/* AI Model Status */}
            <div className="relative bg-gray-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-cyan-700/50">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-cyan-400 uppercase tracking-widest">
                  Modelo LSTM
                </h3>
                <Zap className="w-5 h-5 text-cyan-400" />
              </div>
              <div className="text-2xl font-extrabold text-white mb-2">
                🤖 {backendStatus === 'Funcionando' ? 'Activo' : 'Esperando'}
              </div>
              <div className="text-sm text-gray-400">
                {backendStatus === 'Funcionando' ? 'Red neuronal operativa' : 'Red neuronal en standby'}
              </div>
            </div>
          </div>
        </div>

        {/* Selector de Ciudades */}
        {cities.length > 0 && (
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-white mb-6 text-center">
              🏙️ Selecciona una Ciudad
            </h2>
            <div className="max-w-4xl mx-auto">
              <div className="relative bg-gray-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-cyan-700/50">
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {cities.map((city) => (
                    <button
                      key={city.id}
                      onClick={() => handleCityChange(city.name)}
                      disabled={loadingCityData}
                      className={`
                        p-3 rounded-xl font-medium transition-all duration-300 transform hover:scale-105
                        ${selectedCity === city.name 
                          ? 'bg-cyan-500 text-gray-900 shadow-lg shadow-cyan-500/30' 
                          : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/70 hover:text-white'
                        }
                        ${loadingCityData ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                      `}
                    >
                      {city.name}
                    </button>
                  ))}
                </div>
                {loadingCityData && (
                  <div className="absolute inset-0 bg-gray-900/50 rounded-2xl flex items-center justify-center">
                    <div className="text-white text-lg font-medium">
                      🔄 Cargando datos de {selectedCity}...
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Apartados Específicos de Datos */}
        {airQualityData && (
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-white mb-6 text-center">
              📊 Datos Detallados - {selectedCity}
            </h2>
            
            {/* Fecha Actual */}
            <div className="mb-6">
              <div className="max-w-2xl mx-auto relative bg-gradient-to-r from-indigo-800/70 to-purple-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-indigo-700/50">
                <div className="text-center">
                  <h3 className="text-lg font-medium text-indigo-300 uppercase tracking-widest mb-2">
                    📅 Fecha y Hora Actual
                  </h3>
                  <div className="text-3xl font-extrabold text-white">
                    {new Date().toLocaleDateString('es-ES', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </div>
                  <div className="text-xl text-indigo-200 mt-2">
                    {new Date().toLocaleTimeString('es-ES', { 
                      hour: '2-digit', 
                      minute: '2-digit',
                      second: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* Grid de Datos Específicos */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              
              {/* PM2.5 Actual */}
              <div className="relative bg-gradient-to-br from-red-800/70 to-orange-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-red-700/50">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-4">
                    <div className="w-12 h-12 bg-red-500/30 rounded-full flex items-center justify-center">
                      <span className="text-2xl">🔬</span>
                    </div>
                  </div>
                  <h3 className="text-sm font-medium text-red-300 uppercase tracking-widest mb-2">
                    PM2.5 Actual
                  </h3>
                  <div className="text-4xl font-extrabold text-white mb-2">
                    {airQualityData.current?.pm25 || '--'}
                  </div>
                  <div className="text-red-200 text-sm">
                    μg/m³
                  </div>
                  <div className={`mt-3 px-3 py-1 rounded-full text-xs font-bold ${
                    (airQualityData.current?.pm25 || 0) <= 12 ? 'bg-green-500/80 text-white' :
                    (airQualityData.current?.pm25 || 0) <= 35 ? 'bg-yellow-500/80 text-gray-900' :
                    (airQualityData.current?.pm25 || 0) <= 55 ? 'bg-orange-500/80 text-white' :
                    'bg-red-500/80 text-white'
                  }`}>
                    {airQualityData.current?.quality_level || 'N/A'}
                  </div>
                </div>
              </div>

              {/* PM2.5 Predicho */}
              <div className="relative bg-gradient-to-br from-purple-800/70 to-pink-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-purple-700/50">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-4">
                    <div className="w-12 h-12 bg-purple-500/30 rounded-full flex items-center justify-center">
                      <span className="text-2xl">🤖</span>
                    </div>
                  </div>
                  <h3 className="text-sm font-medium text-purple-300 uppercase tracking-widest mb-2">
                    PM2.5 Predicho (IA)
                  </h3>
                  <div className="text-4xl font-extrabold text-white mb-2">
                    {airQualityData.prediction?.predicted_pm25 || '--'}
                  </div>
                  <div className="text-purple-200 text-sm">
                    μg/m³
                  </div>
                  <div className="mt-3 text-xs text-purple-200">
                    Confianza: {airQualityData.prediction?.confidence ? 
                      `${(airQualityData.prediction.confidence * 100).toFixed(0)}%` : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Temperatura */}
              <div className="relative bg-gradient-to-br from-orange-800/70 to-yellow-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-orange-700/50">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-4">
                    <div className="w-12 h-12 bg-orange-500/30 rounded-full flex items-center justify-center">
                      <span className="text-2xl">🌡️</span>
                    </div>
                  </div>
                  <h3 className="text-sm font-medium text-orange-300 uppercase tracking-widest mb-2">
                    Temperatura
                  </h3>
                  <div className="text-4xl font-extrabold text-white mb-2">
                    {airQualityData.current?.weather?.temperature || '--'}
                  </div>
                  <div className="text-orange-200 text-sm">
                    °Celsius
                  </div>
                  <div className="mt-3 text-xs text-orange-200">
                    {(airQualityData.current?.weather?.temperature || 0) >= 25 ? '🔥 Cálido' :
                     (airQualityData.current?.weather?.temperature || 0) >= 15 ? '🌤️ Templado' :
                     '❄️ Frío'}
                  </div>
                </div>
              </div>

              {/* Humedad */}
              <div className="relative bg-gradient-to-br from-blue-800/70 to-cyan-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-blue-700/50">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-4">
                    <div className="w-12 h-12 bg-blue-500/30 rounded-full flex items-center justify-center">
                      <span className="text-2xl">💧</span>
                    </div>
                  </div>
                  <h3 className="text-sm font-medium text-blue-300 uppercase tracking-widest mb-2">
                    Humedad
                  </h3>
                  <div className="text-4xl font-extrabold text-white mb-2">
                    {airQualityData.current?.weather?.humidity || '--'}
                  </div>
                  <div className="text-blue-200 text-sm">
                    % Relativa
                  </div>
                  <div className="mt-3 text-xs text-blue-200">
                    {(airQualityData.current?.weather?.humidity || 0) >= 70 ? '🌊 Húmedo' :
                     (airQualityData.current?.weather?.humidity || 0) >= 40 ? '🌤️ Normal' :
                     '🏜️ Seco'}
                  </div>
                </div>
              </div>

            </div>

            {/* Resumen AQI */}
            <div className="mt-8">
              <div className="max-w-4xl mx-auto relative bg-gray-800/70 p-6 rounded-2xl shadow-2xl backdrop-blur-sm border border-gray-700">
                <div className="text-center">
                  <h3 className="text-lg font-medium text-gray-300 uppercase tracking-widest mb-4">
                    📈 Índice de Calidad del Aire (AQI)
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <div className="text-2xl font-bold text-white">
                        AQI: {airQualityData.current?.aqi || 'N/A'}
                      </div>
                      <div className="text-gray-400 text-sm mt-1">Índice Actual</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-cyan-400">
                        {selectedCity}
                      </div>
                      <div className="text-gray-400 text-sm mt-1">Ciudad Monitoreada</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-400">
                        {airQualityData.prediction?.prediction_date || 'N/A'}
                      </div>
                      <div className="text-gray-400 text-sm mt-1">Fecha de Predicción</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-16 bg-gray-800/50 p-10 rounded-2xl border border-gray-700 flex flex-col md:flex-row items-center justify-between shadow-xl backdrop-blur-lg">
          <div className="md:max-w-lg">
            <h2 className="text-3xl font-bold text-white">
              Predicciones con IA.
            </h2>
            <p className="mt-2 text-gray-400">
              Nuestro sistema utiliza redes neuronales LSTM para predecir la calidad del aire
              basándose en datos históricos y en tiempo real de {cities.length} ciudades globales.
              Selecciona cualquier ciudad para ver datos actualizados de temperatura, humedad y PM2.5.
            </p>
          </div>
          <div className="flex flex-col space-y-3 mt-6 md:mt-0">
            <button 
              className="px-8 py-3 bg-cyan-500 text-gray-900 font-bold rounded-xl shadow-lg hover:bg-cyan-400 transition transform hover:-translate-y-0.5 duration-300"
              onClick={() => window.open('http://localhost:5000/api/cities', '_blank')}
            >
              Ver API de Datos
            </button>
            <button 
              className="px-8 py-3 bg-purple-500 text-white font-bold rounded-xl shadow-lg hover:bg-purple-400 transition transform hover:-translate-y-0.5 duration-300"
              onClick={() => checkBackendStatus()}
            >
              🔄 Actualizar Datos
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;