// ========================================
// COMPONENTES DE EJEMPLO PARA REACT
// Muestran cómo integrar el backend de calidad del aire
// ========================================

import React, { useState, useEffect } from 'react';
import { 
  useCityData, 
  useCities, 
  usePrediction, 
  useTimeSeries,
  useDashboard,
  useServerHealth,
  useFavorites 
} from './hooks';
import { formatPM25, getAirQualityCategory } from './airQualityAPI';

// ========================================
// COMPONENTE: Dashboard Principal
// ========================================

export const AirQualityDashboard = () => {
  const [selectedCity, setSelectedCity] = useState('Mendoza');
  const { dashboard, loading, error, refetch } = useDashboard(selectedCity);
  const { cities } = useCities();
  const { isOnline } = useServerHealth();

  const handleCityChange = (event) => {
    setSelectedCity(event.target.value);
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <h2>🔄 Cargando datos de {selectedCity}...</h2>
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={refetch}>🔄 Reintentar</button>
      </div>
    );
  }

  const current = dashboard?.current?.data;
  const category = dashboard?.airQualityCategory;
  const trend = dashboard?.trend;

  return (
    <div className="air-quality-dashboard">
      <header className="dashboard-header">
        <h1>🌍 Calidad del Aire</h1>
        <div className="server-status">
          Estado: {isOnline ? '🟢 Conectado' : '🔴 Desconectado'}
        </div>
      </header>

      <div className="city-selector">
        <label htmlFor="city-select">Seleccionar ciudad:</label>
        <select 
          id="city-select" 
          value={selectedCity} 
          onChange={handleCityChange}
        >
          {cities?.data?.cities?.map(city => (
            <option key={city.name} value={city.name}>
              {city.name}, {city.country}
            </option>
          ))}
        </select>
      </div>

      {current && (
        <div className="current-data">
          <div className="main-metric">
            <h2>{selectedCity}</h2>
            <div className="pm25-value" style={{ color: category?.color }}>
              {formatPM25(current.pm25)}
            </div>
            <div className="quality-category" style={{ backgroundColor: category?.color }}>
              {category?.category}
            </div>
          </div>

          <div className="additional-metrics">
            <div className="metric">
              <span className="label">AQI:</span>
              <span className="value">{current.aqi || 'N/A'}</span>
            </div>
            <div className="metric">
              <span className="label">NO2:</span>
              <span className="value">{current.no2 ? `${current.no2} μg/m³` : 'N/A'}</span>
            </div>
            <div className="metric">
              <span className="label">Temperatura:</span>
              <span className="value">{current.temperature ? `${current.temperature}°C` : 'N/A'}</span>
            </div>
          </div>

          {trend && (
            <div className="trend-indicator">
              <span>Tendencia: {trend.direction} </span>
              <span className={`trend-${trend.trend}`}>
                {trend.trend === 'increasing' ? 'Empeorando' : 
                 trend.trend === 'decreasing' ? 'Mejorando' : 'Estable'}
              </span>
            </div>
          )}
        </div>
      )}

      <div className="dashboard-actions">
        <button onClick={refetch}>🔄 Actualizar</button>
      </div>
    </div>
  );
};

// ========================================
// COMPONENTE: Lista de Ciudades
// ========================================

export const CityList = ({ onCitySelect }) => {
  const { data: citiesData, loading, error } = useCities();
  const { favorites, toggleFavorite, isFavorite } = useFavorites();

  if (loading) return <div>🔄 Cargando ciudades...</div>;
  if (error) return <div>❌ Error: {error}</div>;

  const cities = citiesData?.cities || [];

  return (
    <div className="city-list">
      <h3>🏙️ Ciudades Disponibles</h3>
      
      {favorites.length > 0 && (
        <div className="favorites-section">
          <h4>⭐ Favoritas</h4>
          {favorites.map(cityName => (
            <div key={`fav-${cityName}`} className="city-item favorite">
              <span onClick={() => onCitySelect?.(cityName)}>
                {cityName}
              </span>
              <button onClick={() => toggleFavorite(cityName)}>
                ⭐
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="all-cities-section">
        <h4>🌍 Todas las ciudades</h4>
        {cities.map(city => (
          <div key={city.name} className="city-item">
            <span onClick={() => onCitySelect?.(city.name)}>
              {city.name}, {city.country}
            </span>
            <button 
              onClick={() => toggleFavorite(city.name)}
              className={isFavorite(city.name) ? 'favorited' : 'not-favorited'}
            >
              {isFavorite(city.name) ? '⭐' : '☆'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// ========================================
// COMPONENTE: Datos de Ciudad Simple
// ========================================

export const SimpleCityCard = ({ cityName }) => {
  const { cityData, loading, error, refetch } = useCityData(cityName, {
    autoRefresh: true,
    refreshInterval: 60000 // Actualizar cada minuto
  });

  if (loading) {
    return <div className="city-card loading">🔄 Cargando {cityName}...</div>;
  }

  if (error) {
    return (
      <div className="city-card error">
        <h3>{cityName}</h3>
        <p>❌ {error}</p>
        <button onClick={refetch}>Reintentar</button>
      </div>
    );
  }

  const data = cityData?.data;
  const category = cityData?.airQualityCategory;

  return (
    <div className="city-card">
      <h3>{cityName}</h3>
      {data ? (
        <>
          <div className="pm25-display" style={{ color: category?.color }}>
            <span className="value">{formatPM25(data.pm25)}</span>
            <span className="label">PM2.5</span>
          </div>
          <div className="category" style={{ backgroundColor: category?.color }}>
            {category?.category}
          </div>
          <div className="additional-info">
            {data.aqi && <div>AQI: {data.aqi}</div>}
            {data.temperature && <div>🌡️ {data.temperature}°C</div>}
          </div>
        </>
      ) : (
        <div>Sin datos disponibles</div>
      )}
      <button onClick={refetch} className="refresh-btn">🔄</button>
    </div>
  );
};

// ========================================
// COMPONENTE: Predictor
// ========================================

export const PredictionForm = () => {
  const { prediction, loading, error, predictForCity, clearPrediction } = usePrediction();
  const [selectedCity, setSelectedCity] = useState('Mendoza');
  const { data: citiesData } = useCities();

  const handlePredict = async () => {
    try {
      await predictForCity(selectedCity);
    } catch (err) {
      console.error('Error en predicción:', err);
    }
  };

  const cities = citiesData?.cities || [];

  return (
    <div className="prediction-form">
      <h3>🔮 Predictor de Calidad del Aire</h3>
      
      <div className="form-group">
        <label>Ciudad:</label>
        <select 
          value={selectedCity}
          onChange={(e) => setSelectedCity(e.target.value)}
          disabled={loading}
        >
          {cities.map(city => (
            <option key={city.name} value={city.name}>
              {city.name}
            </option>
          ))}
        </select>
      </div>

      <div className="form-actions">
        <button 
          onClick={handlePredict}
          disabled={loading || !selectedCity}
          className="predict-btn"
        >
          {loading ? '🔄 Prediciendo...' : '🎯 Predecir'}
        </button>
        
        {prediction && (
          <button onClick={clearPrediction} className="clear-btn">
            🗑️ Limpiar
          </button>
        )}
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {prediction && (
        <div className="prediction-result">
          <h4>📊 Resultado de la Predicción</h4>
          <div className="prediction-value">
            <span className="label">PM2.5 predicho para mañana:</span>
            <span className="value">
              {formatPM25(prediction.prediction?.pm25_predicted)}
            </span>
          </div>
          <div className="prediction-details">
            <div>📅 Fecha: {prediction.prediction?.prediction_for}</div>
            <div>🎯 Confianza: {prediction.prediction?.confidence}</div>
            <div>🏙️ Ciudad: {selectedCity}</div>
          </div>
        </div>
      )}
    </div>
  );
};

// ========================================
// COMPONENTE: Gráfico Simple (sin Chart.js)
// ========================================

export const SimpleTimeSeriesChart = ({ cityName, days = 7 }) => {
  const { timeSeriesData, loading, error } = useTimeSeries(cityName, days);

  if (loading) return <div>🔄 Cargando gráfico...</div>;
  if (error) return <div>❌ Error: {error}</div>;

  const data = timeSeriesData?.data;
  if (!data?.targets?.length) return <div>Sin datos para graficar</div>;

  // Crear gráfico simple con barras CSS
  const maxValue = Math.max(...data.targets);
  const minValue = Math.min(...data.targets);
  const range = maxValue - minValue || 1;

  return (
    <div className="simple-chart">
      <h4>📈 PM2.5 - Últimos {days} días</h4>
      <div className="chart-container">
        {data.targets.map((value, index) => {
          const height = ((value - minValue) / range) * 100;
          const category = getAirQualityCategory(value);
          
          return (
            <div key={index} className="bar-container">
              <div 
                className="bar"
                style={{
                  height: `${height}%`,
                  backgroundColor: category.color
                }}
                title={`${formatPM25(value)} - ${data.dates?.[index]}`}
              />
              <div className="bar-label">
                {data.dates?.[index]?.split('-')[2] || index + 1}
              </div>
            </div>
          );
        })}
      </div>
      <div className="chart-legend">
        <span>Min: {formatPM25(minValue)}</span>
        <span>Max: {formatPM25(maxValue)}</span>
      </div>
    </div>
  );
};

// ========================================
// COMPONENTE: Estado del Servidor
// ========================================

export const ServerStatus = () => {
  const { health, isOnline, lastCheck } = useServerHealth(10000); // Check cada 10 segundos

  return (
    <div className={`server-status ${isOnline ? 'online' : 'offline'}`}>
      <div className="status-indicator">
        {isOnline ? '🟢' : '🔴'} 
        {isOnline ? 'Conectado' : 'Desconectado'}
      </div>
      
      {health && (
        <div className="health-details">
          <div>Modelo cargado: {health.model_loaded ? '✅' : '❌'}</div>
          <div>Dispositivo: {health.device}</div>
        </div>
      )}
      
      {lastCheck && (
        <div className="last-check">
          Última verificación: {lastCheck.toLocaleTimeString()}
        </div>
      )}
    </div>
  );
};

// ========================================
// COMPONENTE: App de Ejemplo Completa
// ========================================

export const ExampleApp = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedCity, setSelectedCity] = useState('Mendoza');

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <AirQualityDashboard />;
      case 'cities':
        return <CityList onCitySelect={setSelectedCity} />;
      case 'prediction':
        return <PredictionForm />;
      case 'chart':
        return <SimpleTimeSeriesChart cityName={selectedCity} days={14} />;
      default:
        return <AirQualityDashboard />;
    }
  };

  return (
    <div className="air-quality-app">
      <nav className="app-nav">
        <h1>🌍 Calidad del Aire</h1>
        <div className="nav-buttons">
          <button 
            onClick={() => setCurrentView('dashboard')}
            className={currentView === 'dashboard' ? 'active' : ''}
          >
            📊 Dashboard
          </button>
          <button 
            onClick={() => setCurrentView('cities')}
            className={currentView === 'cities' ? 'active' : ''}
          >
            🏙️ Ciudades
          </button>
          <button 
            onClick={() => setCurrentView('prediction')}
            className={currentView === 'prediction' ? 'active' : ''}
          >
            🔮 Predicción
          </button>
          <button 
            onClick={() => setCurrentView('chart')}
            className={currentView === 'chart' ? 'active' : ''}
          >
            📈 Gráficos
          </button>
        </div>
        <ServerStatus />
      </nav>

      <main className="app-content">
        {renderView()}
      </main>
    </div>
  );
};

// Estilos CSS básicos (colocar en un archivo .css separado)
export const basicStyles = `
.air-quality-app {
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.app-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 2px solid #eee;
  margin-bottom: 20px;
}

.nav-buttons {
  display: flex;
  gap: 10px;
}

.nav-buttons button {
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background: #f0f0f0;
}

.nav-buttons button.active {
  background: #007bff;
  color: white;
}

.server-status {
  padding: 10px;
  border-radius: 5px;
  text-align: center;
}

.server-status.online {
  background: #d4edda;
  color: #155724;
}

.server-status.offline {
  background: #f8d7da;
  color: #721c24;
}

.city-card {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 20px;
  margin: 10px;
  text-align: center;
  min-width: 200px;
}

.pm25-display {
  font-size: 2em;
  font-weight: bold;
  margin: 10px 0;
}

.category {
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  margin: 10px 0;
}

.simple-chart {
  margin: 20px 0;
}

.chart-container {
  display: flex;
  align-items: end;
  height: 200px;
  gap: 5px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.bar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar {
  width: 100%;
  min-height: 2px;
  border-radius: 2px 2px 0 0;
}

.bar-label {
  font-size: 0.8em;
  margin-top: 5px;
}

.prediction-form {
  max-width: 500px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
}

.form-group {
  margin: 15px 0;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group select, .form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.predict-btn {
  background: #28a745;
  color: white;
  padding: 12px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.predict-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 5px;
  margin: 10px 0;
}

.prediction-result {
  background: #d4edda;
  color: #155724;
  padding: 20px;
  border-radius: 5px;
  margin: 20px 0;
}

.prediction-value {
  font-size: 1.2em;
  font-weight: bold;
  margin: 10px 0;
}

.prediction-details {
  margin-top: 15px;
}

.prediction-details > div {
  margin: 5px 0;
}
`;

export default ExampleApp;