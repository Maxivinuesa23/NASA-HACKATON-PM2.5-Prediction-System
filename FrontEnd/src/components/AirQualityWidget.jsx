// Componente mejorado de calidad del aire con manejo robusto de errores
import React, { useState, useEffect } from 'react';

// Hook mejorado para datos de calidad del aire
const useAirQualityData = () => {
  const [data, setData] = useState(null);
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('Ciudad de México');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);

  // Función para hacer peticiones seguras
  const safeFetch = async (url, options = {}) => {
    try {
      console.log('Fetching:', url);
      const response = await fetch(url, {
        ...options,
        timeout: 10000,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Response:', data);
      return data;
    } catch (error) {
      console.error('Fetch error:', error);
      throw error;
    }
  };

  // Verificar estado del backend
  const checkBackend = async () => {
    try {
      const result = await safeFetch('http://localhost:5000/api/health');
      setBackendOnline(result.status === 'healthy');
      return true;
    } catch (error) {
      console.log('Backend offline:', error.message);
      setBackendOnline(false);
      return false;
    }
  };

  // Cargar ciudades
  const loadCities = async () => {
    try {
      const result = await safeFetch('http://localhost:5000/api/cities');
      if (result.success && result.cities) {
        setCities(result.cities);
        console.log('Cities loaded:', result.cities.length);
      }
    } catch (error) {
      console.error('Error loading cities:', error);
      // Usar ciudades por defecto si falla
      setCities([
        { id: '1', name: 'Ciudad de México' },
        { id: '2', name: 'Nueva York' },
        { id: '3', name: 'Los Ángeles' },
        { id: '4', name: 'Madrid' },
        { id: '5', name: 'Londres' },
      ]);
    }
  };

  // Cargar datos de ciudad
  const loadCityData = async (cityName) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await safeFetch(`http://localhost:5000/api/cities/${encodeURIComponent(cityName)}`);
      
      if (result.success && result.data) {
        setData(result.data);
        console.log('City data loaded for:', cityName);
      } else {
        throw new Error(result.message || 'No data available');
      }
    } catch (error) {
      console.error('Error loading city data:', error);
      setError(`Error cargando datos de ${cityName}: ${error.message}`);
      
      // Datos de fallback para demostración
      setData({
        current: {
          pm25: 25.0,
          aqi: 75,
          quality_level: 'MODERADA',
          weather: {
            temperature: 22,
            humidity: 60
          }
        },
        prediction: {
          predicted_pm25: 23.5,
          prediction_date: new Date().toISOString().split('T')[0],
          confidence: 0.85
        }
      });
    } finally {
      setLoading(false);
    }
  };

  // Inicialización
  useEffect(() => {
    const initialize = async () => {
      console.log('Initializing component...');
      
      // Verificar backend primero
      await checkBackend();
      
      // Cargar ciudades
      await loadCities();
      
      // Cargar datos iniciales
      await loadCityData(selectedCity);
    };

    initialize();
  }, []);

  // Cargar datos cuando cambia la ciudad
  useEffect(() => {
    if (selectedCity) {
      loadCityData(selectedCity);
    }
  }, [selectedCity]);

  return {
    data,
    cities,
    selectedCity,
    setSelectedCity,
    loading,
    error,
    backendOnline,
    refresh: () => loadCityData(selectedCity)
  };
};

// Componente principal mejorado
export const AirQualityWidget = () => {
  const {
    data,
    cities,
    selectedCity,
    setSelectedCity,
    loading,
    error,
    backendOnline,
    refresh
  } = useAirQualityData();

  // Estilos en línea para evitar dependencias CSS
  const styles = {
    container: {
      maxWidth: '1200px',
      margin: '20px auto',
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      backgroundColor: '#f8fafc',
      minHeight: '600px'
    },
    header: {
      textAlign: 'center',
      marginBottom: '30px'
    },
    title: {
      fontSize: '2.5rem',
      marginBottom: '10px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      backgroundClip: 'text',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      color: '#374151' // Fallback
    },
    status: {
      position: 'fixed',
      top: '20px',
      right: '20px',
      padding: '10px 20px',
      borderRadius: '20px',
      color: 'white',
      fontWeight: 'bold',
      zIndex: 1000,
      backgroundColor: backendOnline ? '#10B981' : '#EF4444'
    },
    citySelector: {
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      marginBottom: '30px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    },
    cityButton: (isSelected) => ({
      background: isSelected ? '#667eea' : 'white',
      color: isSelected ? 'white' : '#374151',
      border: '2px solid #667eea',
      borderRadius: '25px',
      padding: '10px 20px',
      margin: '5px',
      cursor: 'pointer',
      fontWeight: '500',
      display: 'inline-block'
    }),
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '20px',
      marginBottom: '30px'
    },
    card: {
      background: 'white',
      borderRadius: '15px',
      padding: '20px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      border: '2px solid #E5E7EB'
    },
    cardHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '15px'
    },
    cardValue: {
      fontSize: '2.5rem',
      fontWeight: 'bold',
      color: '#374151'
    },
    loading: {
      textAlign: 'center',
      padding: '40px'
    },
    spinner: {
      border: '4px solid #f3f4f6',
      borderTop: '4px solid #667eea',
      borderRadius: '50%',
      width: '40px',
      height: '40px',
      animation: 'spin 1s linear infinite',
      margin: '0 auto 20px'
    },
    error: {
      background: '#FEF2F2',
      border: '1px solid #FECACA',
      borderRadius: '10px',
      padding: '20px',
      textAlign: 'center',
      color: '#DC2626'
    },
    button: {
      background: '#667eea',
      color: 'white',
      border: 'none',
      padding: '10px 20px',
      borderRadius: '8px',
      cursor: 'pointer',
      marginTop: '10px'
    }
  };

  // Agregar animación CSS
  React.useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  console.log('Rendering component - Loading:', loading, 'Error:', error, 'Data:', !!data);

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>
          <div style={styles.spinner}></div>
          <p>Cargando datos de calidad del aire...</p>
          <p>Backend: {backendOnline ? 'Conectado' : 'Conectando...'}</p>
        </div>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>
          <h3>⚠️ Error de Conexión</h3>
          <p>{error}</p>
          <p>Backend: {backendOnline ? 'Conectado' : 'Desconectado'}</p>
          <button style={styles.button} onClick={refresh}>
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Estado del backend */}
      <div style={styles.status}>
        {backendOnline ? '✅ Backend Conectado' : '❌ Backend Desconectado'}
      </div>

      {/* Encabezado */}
      <div style={styles.header}>
        <h1 style={styles.title}>🌍 Monitor de Calidad del Aire</h1>
        <p style={{ color: '#6B7280' }}>Datos en tiempo real y predicciones con IA</p>
      </div>

      {/* Selector de ciudades */}
      <div style={styles.citySelector}>
        <h3 style={{ marginBottom: '15px' }}>🏙️ Selecciona una ciudad:</h3>
        <div>
          {cities.map((city) => (
            <button
              key={city.id}
              style={styles.cityButton(selectedCity === city.name)}
              onClick={() => setSelectedCity(city.name)}
            >
              {city.name}
            </button>
          ))}
        </div>
      </div>

      {/* Mostrar error si existe pero tenemos datos */}
      {error && (
        <div style={{...styles.error, marginBottom: '20px'}}>
          <p>⚠️ {error}</p>
          <p>Mostrando datos de respaldo</p>
        </div>
      )}

      {/* Tarjetas de datos */}
      {data && (
        <>
          <div style={styles.grid}>
            {/* PM2.5 Actual */}
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <h4 style={{ margin: 0, color: '#6B7280' }}>PM2.5 Actual</h4>
                <span style={{ fontSize: '1.5rem' }}>🔬</span>
              </div>
              <div style={styles.cardValue}>
                {data.current?.pm25 || '--'}
                <span style={{ fontSize: '1rem', color: '#9CA3AF', marginLeft: '5px' }}>
                  μg/m³
                </span>
              </div>
              {data.current?.quality_level && (
                <div style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  borderRadius: '15px',
                  backgroundColor: '#10B981',
                  color: 'white',
                  fontSize: '0.8rem',
                  marginTop: '10px'
                }}>
                  {data.current.quality_level}
                </div>
              )}
            </div>

            {/* Predicción IA */}
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <h4 style={{ margin: 0, color: '#6B7280' }}>Predicción IA</h4>
                <span style={{ fontSize: '1.5rem' }}>🤖</span>
              </div>
              <div style={styles.cardValue}>
                {data.prediction?.predicted_pm25 || '--'}
                <span style={{ fontSize: '1rem', color: '#9CA3AF', marginLeft: '5px' }}>
                  μg/m³
                </span>
              </div>
              <div style={{ fontSize: '0.8rem', color: '#6B7280', marginTop: '10px' }}>
                Para: {data.prediction?.prediction_date || 'N/A'}
              </div>
            </div>

            {/* Temperatura */}
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <h4 style={{ margin: 0, color: '#6B7280' }}>Temperatura</h4>
                <span style={{ fontSize: '1.5rem' }}>🌡️</span>
              </div>
              <div style={styles.cardValue}>
                {data.current?.weather?.temperature || '--'}
                <span style={{ fontSize: '1rem', color: '#9CA3AF', marginLeft: '5px' }}>
                  °C
                </span>
              </div>
            </div>

            {/* Humedad */}
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <h4 style={{ margin: 0, color: '#6B7280' }}>Humedad</h4>
                <span style={{ fontSize: '1.5rem' }}>💧</span>
              </div>
              <div style={styles.cardValue}>
                {data.current?.weather?.humidity || '--'}
                <span style={{ fontSize: '1rem', color: '#9CA3AF', marginLeft: '5px' }}>
                  %
                </span>
              </div>
            </div>
          </div>

          {/* Información adicional */}
          <div style={styles.card}>
            <h3 style={{ marginBottom: '15px' }}>📊 Información Adicional</h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '15px'
            }}>
              <div><strong>AQI:</strong> {data.current?.aqi || 'N/A'}</div>
              <div><strong>Ciudad:</strong> {selectedCity}</div>
              <div><strong>Predicción para:</strong> {data.prediction?.prediction_date || 'N/A'}</div>
              <div><strong>Confianza:</strong> {data.prediction?.confidence ? `${(data.prediction.confidence * 100).toFixed(0)}%` : 'N/A'}</div>
            </div>
            
            <button style={{...styles.button, marginTop: '15px'}} onClick={refresh}>
              🔄 Actualizar Datos
            </button>
          </div>
        </>
      )}
    </div>
  );
};

// Exportar también como default
export default AirQualityWidget;