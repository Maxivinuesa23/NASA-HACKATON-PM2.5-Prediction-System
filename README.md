# 🌬️ Predictor de Calidad del Aire con AirVisual API

Un sistema de predicción de calidad del aire que utiliza redes neuronales LSTM y datos en tiempo real de la API de AirVisual (IQAir).

## 🚀 Características

- ✅ **API de AirVisual**: Datos reales y actualizados de calidad del aire
- ✅ **6 Ciudades**: Ciudad de México, Nueva York, Los Ángeles, Madrid, Londres, Buenos Aires
- ✅ **Predicciones LSTM**: Red neuronal entrenada con PyTorch
- ✅ **Datos Únicos por Ciudad**: Cada ciudad tiene perfiles específicos de contaminación
- ✅ **Fallback Inteligente**: Datos sintéticos específicos si la API no está disponible
- ✅ **Interfaz Intuitiva**: Menú de selección de ciudades con emojis

## 📊 Métricas de Predicción

- **PM2.5**: Partículas finas (μg/m³)
- **NO2**: Dióxido de nitrógeno (μg/m³)
- **AQI**: Índice de calidad del aire
- **Tendencias**: Mejorando/Empeorando con diferencias

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8+
- API Key de AirVisual (gratuita en https://www.iqair.com/air-quality-monitors/api)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd predictor-calidad-aire
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar API Key**
Edita el archivo `config.py` y reemplaza el valor de `AIRVISUAL_API_KEY`:
```python
AIRVISUAL_API_KEY = "TU_API_KEY_AQUI"
```

4. **Ejecutar el sistema**
```bash
python ScriptInicial.py
```

## 📁 Estructura del Proyecto

```
predictor-calidad-aire/
├── ScriptInicial.py           # Script principal de ejecución
├── AirVisualSimulator.py      # Módulo de integración con AirVisual API
├── ModeloLSTM.py              # Arquitectura y entrenamiento del modelo LSTM
├── config.py                  # Configuración de API keys
├── requirements.txt           # Dependencias de Python
└── README.md                  # Este archivo
```

## 🌍 Ciudades Disponibles

| Ciudad | País | Factores de Ajuste |
|--------|------|-------------------|
| Ciudad de México | México | Factor: 1.3 (Más contaminada) |
| Nueva York | USA | Factor: 0.8 (Menos contaminada) |
| Los Ángeles | USA | Factor: 1.0 (Moderada) |
| Madrid | España | Factor: 0.9 (Europea, más limpia) |
| Londres | Reino Unido | Factor: 0.7 (Muy regulada) |
| Buenos Aires | Argentina | Factor: 1.1 (Similar a base) |

## 🧠 Modelo LSTM

### Arquitectura
- **Capas**: 2 capas LSTM con 128 unidades ocultas
- **Dropout**: 0.2 para prevenir overfitting
- **Secuencias**: 10 días de historial para predecir el siguiente día
- **Características**: PM2.5 y NO2

### Entrenamiento
- **Optimizador**: Adam con learning rate 0.001
- **Función de pérdida**: MSE (Mean Squared Error)
- **Épocas**: 30
- **Validación**: 20% de los datos

## 🔄 Flujo de Trabajo

1. **Selección de Ciudad**: El usuario elige una de las 6 ciudades disponibles
2. **Obtención de Datos**: 
   - Primero intenta obtener datos de la ciudad específica desde AirVisual API
   - Si no hay datos, usa ciudades de respaldo (Beijing, Delhi, Tokyo, London, Paris)
   - Como último recurso, genera datos sintéticos específicos por ciudad
3. **Ajuste por Ciudad**: Aplica factores únicos para hacer cada ciudad diferente
4. **Entrenamiento**: Entrena el modelo LSTM con los datos obtenidos
5. **Predicción**: Genera predicción para el día siguiente
6. **Visualización**: Muestra resultados con análisis de tendencias

## 📈 Ejemplo de Salida

```
🤖 PREDICTOR DE CALIDAD DEL AIRE
==================================================
📅 Fecha actual: 2025-10-03
🔮 Predicción para: 2025-10-04
==================================================

🌍 CIUDADES DISPONIBLES:
------------------------------
1. Ciudad de México
2. Nueva York
3. Los Ángeles
4. Madrid
5. Londres
6. Buenos Aires

🏙️  Elige una ciudad (1-6): 2
✅ Has seleccionado: Nueva York

📊 Obteniendo datos...
🏙️  Obteniendo datos para: Nueva York
   🌍 Consultando AirVisual API para Nueva York...
   ✅ Datos obtenidos exitosamente!
   📊 AQI US: 45
   🌫️  PM2.5: 18 μg/m³
   🔧 Ajustando PM2.5 para Nueva York: 18.0 → 14.4 μg/m³

🔮 PREDICCIÓN PARA NUEVA YORK - 2025-10-04
--------------------------------------------------
📊 PM2.5 actual (hoy): 18.0 μg/m³
🎯 PM2.5 predicho (mañana): 15.9 μg/m³
📋 Calidad del aire: BUENA 🟢
📈 Tendencia: MEJORANDO ⬇️ (-2.1)
```

## 🔧 Configuración Avanzada

### Modificar Ciudades
Para agregar nuevas ciudades, edita el diccionario `CITIES` en `AirVisualSimulator.py`:

```python
CITIES = {
    "7": {
        "name": "Nueva Ciudad",
        "city": "New City",
        "state": "State Name",
        "country": "Country"
    }
}
```

### Ajustar Factores de Contaminación
Modifica los factores en la función `generate_airvisual_data()`:

```python
city_adjustments = {
    "Nueva Ciudad": {"pm25_factor": 1.1, "pm25_offset": 2}
}
```

## 🚨 Solución de Problemas

### Error: "city_not_found"
- La ciudad no está disponible en AirVisual API
- El sistema automáticamente usa ciudades de respaldo
- Verifica que los nombres de ciudad/estado/país sean correctos

### Error: "Too Many Requests"
- Has excedido el límite de la API (5 req/min para plan gratuito)
- Espera unos minutos antes de ejecutar nuevamente
- Considera actualizar a un plan premium

### Error: SCALER no inicializado
- Elimina el archivo `air_quality_predictor_model.pth`
- Ejecuta el script nuevamente para entrenar un modelo nuevo

## 📝 Cambios Recientes

### v2.0.0 - Migración a AirVisual API
- ✅ Reemplazada OpenAQ API por AirVisual API (IQAir)
- ✅ Simplificada arquitectura del modelo (2 características en lugar de 5)
- ✅ Mejorado sistema de fallback con datos sintéticos específicos
- ✅ Optimizada gestión de rate limits
- ✅ Actualizada documentación completa

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🔗 Enlaces Útiles

- [AirVisual API Documentation](https://www.iqair.com/air-quality-monitors/api)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Calidad del aire - WHO Guidelines](https://www.who.int/news-room/feature-stories/detail/what-are-the-who-air-quality-guidelines)