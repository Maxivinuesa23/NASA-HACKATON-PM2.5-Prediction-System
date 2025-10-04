# 🌍 CloudBusters Air Quality Monitor

Sistema de monitoreo de calidad del aire con inteligencia artificial usando React + Vite y redes neuronales LSTM.

## 🚀 Deploy en Vercel

### Opción 1: Deploy desde GitHub
1. Haz push de tu código a GitHub
2. Ve a [vercel.com](https://vercel.com) e importa tu repositorio
3. Vercel detectará automáticamente que es un proyecto React
4. El deploy se realizará automáticamente

### Opción 2: Deploy con Vercel CLI
```bash
npm i -g vercel
cd FrontEnd
vercel --prod
```

## 📁 Estructura del Proyecto

```
├── FrontEnd/          # Frontend React + Vite
│   ├── src/
│   │   ├── App.jsx               # Aplicación principal
│   │   ├── AtmosphereEffect.jsx  # Efecto de estrellas
│   │   ├── MetricCard.jsx        # Tarjetas de métricas
│   │   ├── Navbar.jsx            # Barra de navegación
│   │   └── services/
│   │       └── airQualityAPI.js  # API con fallback data
│   ├── package.json
│   └── vercel.json
├── app.py             # Backend Flask (solo local)
├── ModeloLSTM.py      # Modelo de IA
└── vercel.json        # Configuración Vercel
```

## 🎯 Funcionalidades

### ✅ Frontend (Desplegado en Vercel)
- **Diseño espacial** con partículas animadas
- **Selector de ciudades** interactivo (7 ciudades globales)
- **Datos en tiempo real**: PM2.5, temperatura, humedad
- **Predicciones IA** con modelo LSTM
- **Responsive design** para móvil y desktop
- **Modo demo** con datos simulados en producción

### 🔧 Backend (Solo local)
- **API Flask** con endpoints REST
- **Modelo LSTM** entrenado con PyTorch
- **AirVisual API** para datos reales
- **7 ciudades monitoreadas**: Ciudad de México, Nueva York, Los Ángeles, Madrid, Londres, Mendoza, Aksu

## 🌐 URLs

- **Producción**: https://tu-deploy-url.vercel.app
- **Local Frontend**: http://localhost:5173
- **Local Backend**: http://localhost:5000

## 🛠️ Desarrollo Local

### Frontend
```bash
cd FrontEnd
npm install
npm run dev
```

### Backend
```bash
pip install -r requirements.txt
python app.py
```

## 📊 Datos en Producción

En Vercel, la aplicación usa **datos simulados** ya que Vercel no soporta Python/Flask. Los datos incluyen:
- PM2.5 actual y predicho
- Temperatura y humedad
- Índice de calidad del aire (AQI)
- 7 ciudades con datos realistas

## 🔧 Configuración de Vercel

El proyecto está configurado para:
- ✅ **Build automático** con Vite
- ✅ **Routing SPA** con rewrites
- ✅ **Cache optimizado** para assets
- ✅ **Fallback data** para modo demo

## 🎨 Tecnologías

- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons
- **Backend**: Flask, PyTorch, AirVisual API
- **Deploy**: Vercel (Frontend), Local (Backend)
- **IA**: LSTM Neural Network para predicciones

## 📱 Responsive

La aplicación es completamente responsive:
- **Desktop**: Grid de 4 columnas
- **Tablet**: Grid de 2-3 columnas  
- **Móvil**: Grid de 1-2 columnas

## 🔄 Modo Híbrido

La aplicación funciona en dos modos:
1. **Local**: Conecta con backend Flask para datos reales
2. **Producción**: Usa datos simulados con la misma interfaz

---

## 🚀 ¡Lista para Deploy!

Tu aplicación está optimizada para Vercel con:
- ✅ Configuración automática
- ✅ Datos de fallback
- ✅ Performance optimizada
- ✅ Zero-config deployment