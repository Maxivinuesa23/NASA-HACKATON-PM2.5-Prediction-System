# 🔗 GUÍA DE INTEGRACIÓN FRONTEND-BACKEND

## 📋 Instrucciones para conectar tu React Frontend

### 📂 **PASO 1: Copiar archivos al frontend**

Copia estos archivos a tu proyecto React en `C:\Users\maxi-\Desktop\Hackaton\Front\FE-CB\cloudbusters\src\`:

```
src/
├── services/
│   ├── airQualityAPI.js     (Servicio principal de API)
│   └── hooks.js             (Hooks personalizados)
├── components/
│   └── examples/
│       └── AirQuality.js    (Componentes de ejemplo)
├── .env.development         (Variables de entorno)
└── .env.production          (Variables de entorno prod)
```

### 🔧 **PASO 2: Instalar dependencias**

En tu proyecto React ejecuta:

```bash
cd C:\Users\maxi-\Desktop\Hackaton\Front\FE-CB\cloudbusters
npm install axios
npm install chart.js react-chartjs-2  # (opcional, para gráficos)
```

### ⚙️ **PASO 3: Configurar package.json**

Agrega esta línea a tu `package.json` para desarrollo local:

```json
{
  "proxy": "http://localhost:5000",
  "dependencies": {
    "axios": "^1.5.0"
  }
}
```

### 🌐 **PASO 4: Variables de entorno**

Crea `.env.development` en la raíz de tu proyecto:

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_DEBUG=true
REACT_APP_DEFAULT_CITY=Mendoza
```

---

## 🚀 **PASO 5: Usar en tus componentes**

### **Ejemplo básico:**

```jsx
import React from 'react';
import { useCityData } from './services/hooks';
import { formatPM25 } from './services/airQualityAPI';

function AirQualityWidget() {
  const { cityData, loading, error } = useCityData('Mendoza');

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Calidad del Aire en Mendoza</h2>
      <p>PM2.5: {formatPM25(cityData?.data?.pm25)}</p>
    </div>
  );
}
```

### **Dashboard completo:**

```jsx
import React, { useState } from 'react';
import { useDashboard, useCities } from './services/hooks';

function Dashboard() {
  const [selectedCity, setSelectedCity] = useState('Mendoza');
  const { dashboard, loading } = useDashboard(selectedCity);
  const { data: cities } = useCities();

  return (
    <div>
      <select value={selectedCity} onChange={(e) => setSelectedCity(e.target.value)}>
        {cities?.cities?.map(city => (
          <option key={city.name} value={city.name}>
            {city.name}
          </option>
        ))}
      </select>
      
      {dashboard && (
        <div>
          <h1>{selectedCity}</h1>
          <p>PM2.5: {dashboard.current?.data?.pm25} μg/m³</p>
          <p>Calidad: {dashboard.airQualityCategory?.category}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🔮 **FUNCIONES PRINCIPALES DISPONIBLES**

### **🏙️ Datos de ciudades:**
```jsx
const { data: cities } = useCities();
const { cityData, loading, error } = useCityData('Mendoza');
```

### **📊 Predicciones:**
```jsx
const { prediction, makePrediction, predictForCity } = usePrediction();

// Predicción automática
await predictForCity('Mendoza');

// Predicción manual
await makePrediction([[10.5, 20.1], /* ... 9 días más */]);
```

### **📈 Datos históricos:**
```jsx
const { timeSeriesData, chartData } = useTimeSeries('Mendoza', 30);
```

### **🎛️ Dashboard completo:**
```jsx
const { dashboard, loading, error } = useDashboard('Mendoza');
```

---

## 🎨 **ESTILOS CSS INCLUIDOS**

Los componentes incluyen estilos básicos. Para personalizarlos, crea un archivo CSS:

```css
/* AirQuality.css */
.air-quality-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.city-card {
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 20px;
  margin: 10px;
  text-align: center;
}

.pm25-display {
  font-size: 2em;
  font-weight: bold;
  margin: 10px 0;
}

.server-status.online {
  background: #d4edda;
  color: #155724;
}

.server-status.offline {
  background: #f8d7da;
  color: #721c24;
}
```

---

## 🔗 **INTEGRACIÓN CON TU PROYECTO EXISTENTE**

### **1. Si tienes un componente principal:**

```jsx
import React from 'react';
import { AirQualityDashboard } from './components/examples/AirQuality';

function App() {
  return (
    <div className="App">
      {/* Tu contenido existente */}
      
      <AirQualityDashboard />
      
      {/* Más contenido */}
    </div>
  );
}
```

### **2. Si usas React Router:**

```jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AirQualityDashboard, PredictionForm } from './components/examples/AirQuality';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/air-quality" element={<AirQualityDashboard />} />
        <Route path="/predictions" element={<PredictionForm />} />
      </Routes>
    </Router>
  );
}
```

### **3. Si usas Context/Redux:**

```jsx
import React, { createContext, useContext } from 'react';
import { useServerHealth } from './services/hooks';

const AirQualityContext = createContext();

export function AirQualityProvider({ children }) {
  const serverHealth = useServerHealth();
  
  return (
    <AirQualityContext.Provider value={{ serverHealth }}>
      {children}
    </AirQualityContext.Provider>
  );
}

export const useAirQualityContext = () => useContext(AirQualityContext);
```

---

## 🚦 **INICIAR DESARROLLO**

### **1. Iniciar backend:**
```bash
cd C:\Users\maxi-\Desktop\Hackaton\ppp
python start_server.py
```

### **2. Iniciar frontend:**
```bash
cd C:\Users\maxi-\Desktop\Hackaton\Front\FE-CB\cloudbusters
npm start
```

### **3. Verificar conexión:**
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- API Docs: http://localhost:5000/api/health

---

## 🛠️ **SOLUCIÓN DE PROBLEMAS**

### **Error CORS:**
```
Access to fetch at 'http://localhost:5000' blocked by CORS
```
**Solución:** El backend ya tiene CORS habilitado. Verifica que esté ejecutándose.

### **Error de conexión:**
```
Network Error
```
**Solución:** 
1. Verifica que el backend esté ejecutándose en puerto 5000
2. Verifica que las variables de entorno estén configuradas
3. Usa `proxy` en package.json para desarrollo

### **Error en predicciones:**
```
Formato incorrecto
```
**Solución:** Asegúrate de enviar exactamente 10 días con 2 valores [PM2.5, NO2]

---

## 📞 **SOPORTE**

- 📖 **API Docs:** `API_DOCUMENTATION.md`
- 🧪 **Probar backend:** `python test_api.py`
- 💻 **Demo:** Abrir `demo.html` en navegador
- 🏥 **Health check:** http://localhost:5000/api/health

---

## 🎯 **PRÓXIMOS PASOS**

1. ✅ Copiar archivos al proyecto React
2. ✅ Instalar dependencias
3. ✅ Configurar variables de entorno
4. ✅ Iniciar backend y frontend
5. ✅ Integrar componentes en tu UI existente
6. ✅ Personalizar estilos según tu diseño
7. ✅ Agregar funcionalidades específicas

**¡Tu frontend React está listo para conectarse con el backend de IA! 🚀🌍**