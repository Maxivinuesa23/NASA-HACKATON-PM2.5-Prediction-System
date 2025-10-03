# ========================================
# SCRIPT PRINCIPAL DEL PREDICTOR DE CALIDAD DEL AIRE
# Coordinador principal que ejecuta todo el sistema
# ========================================

# CONFIGURACIÓN DE IMPORTACIONES
import sys                             # Para manipular el sistema (rutas de Python)
import os                              # Para operaciones del sistema operativo (rutas de archivos)

# CONFIGURAR RUTA DE IMPORTACIONES
current_dir = os.path.dirname(os.path.abspath(__file__))  # Obtiene directorio actual del script
sys.path.insert(0, current_dir)       # Agrega directorio actual al path de Python

# IMPORTACIONES DE MACHINE LEARNING
import torch                           # Framework principal de machine learning
from torch.utils.data import DataLoader, random_split  # Para cargar datos y dividir en train/test
import numpy as np                     # Para operaciones matemáticas
import matplotlib.pyplot as plt        # Para crear gráficos (opcional)
from datetime import datetime, timedelta  # Para manejo de fechas

# IMPORTACIONES DE NUESTRO PROYECTO
from AirVisualSimulator import generate_airvisual_data, AirQualityDataset, SEQ_LENGTH, N_FEATURES, SCALER, select_city
# ↑ Funciones para obtener datos y crear dataset
from ModeloLSTM import AirQualityPredictor, train_model, make_single_prediction, HIDDEN_DIM, NUM_LAYERS, OUTPUT_DIM, BATCH_SIZE, DROPOUT_RATE
# ↑ Modelo LSTM y funciones de entrenamiento

# CONFIGURACIÓN GLOBAL
MODEL_PATH = 'air_quality_predictor_model.pth'  # Archivo donde se guarda el modelo entrenado

def plot_training_history(history):
    """
    FUNCIÓN: Crea gráfico del progreso de entrenamiento del modelo
    PROPÓSITO: Visualizar si el modelo está aprendiendo correctamente
    PARÁMETRO: history (diccionario con pérdidas de entrenamiento y validación)
    """
    plt.figure(figsize=(10, 5))        # Crea figura de 10x5 pulgadas
    plt.plot(history['train_loss'], label='Pérdida Entrenamiento (MSE)', color='skyblue')  # Línea azul para entrenamiento
    plt.plot(history['val_loss'], label='Pérdida Validación (MSE)', color='tomato')        # Línea roja para validación
    plt.title('Historial de Pérdida del Modelo (Error Cuadrático Medio)')  # Título del gráfico
    plt.xlabel('Época')                # Etiqueta eje X (cada época = ciclo completo de entrenamiento)
    plt.ylabel('Pérdida (MSE)')        # Etiqueta eje Y (menor pérdida = mejor modelo)
    plt.legend()                       # Muestra leyenda con colores
    plt.grid(True)                     # Agrega cuadrícula para facilitar lectura
    plt.show()                         # Muestra el gráfico en pantalla

def plot_predictions(targets_scaled, predictions_scaled, title="Predicciones vs. Reales (Conjunto de Validación)"):
    """
    FUNCIÓN: Crea gráfico comparando predicciones del modelo vs valores reales
    PROPÓSITO: Verificar visualmente qué tan bien predice el modelo
    PARÁMETROS: targets_scaled (valores reales), predictions_scaled (predicciones del modelo)
    """
    # IMPORTAR SCALER PARA DESNORMALIZAR
    from AirVisualSimulator import SCALER  # Importa el objeto que normalizó los datos
    
    # DESNORMALIZAR DATOS (convertir de 0-1 de vuelta a μg/m³)
    mean_pm25 = SCALER.mean_[1]        # Media usada para normalizar PM2.5 (columna 1)
    scale_pm25 = SCALER.scale_[1]      # Escala usada para normalizar PM2.5
    
    # FÓRMULA DE DESNORMALIZACIÓN: valor_original = (valor_normalizado * escala) + media
    targets = (targets_scaled * scale_pm25) + mean_pm25      # Valores reales desnormalizados
    predictions = (predictions_scaled * scale_pm25) + mean_pm25  # Predicciones desnormalizadas
    
    # CREAR GRÁFICO
    plt.figure(figsize=(12, 6))        # Figura de 12x6 pulgadas
    plt.plot(targets, label='Valores Reales (PM2.5)', color='darkgreen', linewidth=2)      # Línea verde gruesa = real
    plt.plot(predictions, label='Predicciones del Modelo', color='orange', linestyle='--', alpha=0.7)  # Línea naranja punteada = predicción
    
    # CONFIGURAR GRÁFICO
    plt.title(title)                   # Título personalizable
    plt.xlabel('Muestra (Día)')        # Eje X = días
    plt.ylabel('Concentración de PM2.5 ($\\mu g/m^3$)')  # Eje Y = concentración en μg/m³
    plt.legend()                       # Leyenda
    plt.grid(True, linestyle=':', alpha=0.6)  # Cuadrícula punteada suave
    plt.show()                         # Muestra gráfico


def main():
    """
    FUNCIÓN PRINCIPAL: Controla todo el flujo del programa
    PROPÓSITO: Coordinar datos, entrenamiento y predicción
    FLUJO: 1° Obtener datos → 2° Entrenar modelo → 3° Predecir mañana
    """
    
    # CONFIGURAR FECHAS
    today = datetime.now().date()      # Fecha de hoy
    tomorrow = today + timedelta(days=1)  # Fecha de mañana
    
    # MOSTRAR CABECERA DEL PROGRAMA
    print("🤖 PREDICTOR DE CALIDAD DEL AIRE")
    print("="*50)
    print(f"📅 Fecha actual: {today}")
    print(f"🔮 Predicción para: {tomorrow}")
    print("="*50)
    
    # PASO 1: SELECCIÓN DE CIUDAD
    selected_city = select_city()      # Llama función que muestra menú y obtiene elección del usuario
    
    # PASO 2: OBTENCIÓN DE DATOS
    print("\n📊 Obteniendo datos...")  # Muestra mensaje al usuario
    raw_data_scaled = generate_airvisual_data(selected_city)  # Obtiene datos reales o sintéticos
    
    # VERIFICAR QUE HAY SUFICIENTES DATOS
    if raw_data_scaled is not None and len(raw_data_scaled) >= SEQ_LENGTH + 50:  # Necesita al menos 60 días
        print("✅ Datos obtenidos exitosamente!")  # Confirma éxito
    else:                              # Si no hay suficientes datos
        print("❌ Error: No se pudieron obtener suficientes datos")
        return                         # Termina la función (sale del programa)
    
    # PASO 3: PREPARAR DATOS PARA MACHINE LEARNING
    full_dataset = AirQualityDataset(raw_data_scaled, SEQ_LENGTH)  # Convierte DataFrame a Dataset de PyTorch
    
    # DIVIDIR DATOS: 80% entrenamiento, 20% validación
    train_size = int(0.8 * len(full_dataset))  # 80% de los datos para entrenar
    val_size = len(full_dataset) - train_size  # 20% restante para validar
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])  # División aleatoria

    # CREAR CARGADORES DE DATOS (DataLoaders)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)   # Entrenamiento: mezcla datos
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)      # Validación: orden fijo

    # MOSTRAR INFORMACIÓN DE DATOS
    print(f"📈 Entrenamiento: {len(train_dataset)} secuencias")  # Cuántas secuencias para entrenar
    print(f"📊 Validación: {len(val_dataset)} secuencias")      # Cuántas secuencias para validar
    
    # PASO 4: CREAR Y CARGAR MODELO DE MACHINE LEARNING
    print("\n🧠 Preparando modelo LSTM...")  # Informa al usuario
    model = AirQualityPredictor(N_FEATURES, HIDDEN_DIM, NUM_LAYERS, OUTPUT_DIM, DROPOUT_RATE)  # Crea modelo LSTM
    
    try:                               # Intenta cargar modelo ya entrenado
        model.load_state_dict(torch.load(MODEL_PATH))  # Carga pesos del archivo .pth
        print("✅ Modelo cargado desde archivo")  # Confirma carga exitosa
    except FileNotFoundError:          # Si no existe archivo del modelo
        print("🔄 Entrenando nuevo modelo...")  # Informa que va a entrenar
        train_model(model, train_loader, val_loader)  # Entrena modelo desde cero
        
        # GUARDAR MODELO ENTRENADO
        torch.save(model.state_dict(), MODEL_PATH)  # Guarda pesos en archivo .pth
        print("💾 Modelo guardado")            # Confirma guardado

    # PASO 5: REALIZAR PREDICCIÓN PARA MAÑANA
    print(f"\n🔮 PREDICCIÓN PARA {selected_city['name'].upper()} - {tomorrow}")
    print("-"*50)
    
    # OBTENER ÚLTIMA SECUENCIA DE DATOS (para predecir mañana)
    last_sequence_data, _ = full_dataset[len(full_dataset)-1]  # Últimos 10 días del dataset
    prediction_sequence = last_sequence_data.cpu().numpy()    # Convierte a array de NumPy
    
    # OBTENER VALOR REAL DEL ÚLTIMO DÍA (para referencia)
    from AirVisualSimulator import SCALER  # Importa objeto normalizador
    if SCALER is not None:             # Si el normalizador existe
        # DESNORMALIZAR EL ÚLTIMO VALOR
        last_pm25_scaled = full_dataset.data[-1][1].item()  # PM2.5 del último día (columna 1, normalizado)
        mean_pm25 = SCALER.mean_[1]    # Media usada para normalizar
        scale_pm25 = SCALER.scale_[1]  # Escala usada para normalizar
        real_last_value = (last_pm25_scaled * scale_pm25) + mean_pm25  # Desnormaliza: valor real
    else:                              # Si no hay normalizador
        real_last_value = 25.0         # Valor por defecto
    
    # HACER PREDICCIÓN PARA MAÑANA
    predicted_pm25 = make_single_prediction(model, prediction_sequence)  # Llama al modelo con últimos 10 días
    
    # MOSTRAR RESULTADOS AL USUARIO
    print(f"📊 PM2.5 actual (hoy): {real_last_value:.1f} μg/m³")    # Valor de hoy (.1f = 1 decimal)
    print(f"🎯 PM2.5 predicho (mañana): {predicted_pm25:.1f} μg/m³")  # Predicción para mañana
    
    # CLASIFICAR CALIDAD DEL AIRE SEGÚN VALOR PREDICHO
    if predicted_pm25 <= 12:           # Rango 1: Excelente
        nivel = "BUENA 🟢"            # Verde = aire limpio
    elif predicted_pm25 <= 35:         # Rango 2: Moderado
        nivel = "MODERADA 🟡"         # Amarillo = aceptable
    elif predicted_pm25 <= 55:         # Rango 3: Dañino para sensibles
        nivel = "DAÑINA GRUPOS SENSIBLES 🟠"  # Naranja = cuidado
    elif predicted_pm25 <= 150:        # Rango 4: Dañino para todos
        nivel = "DAÑINA 🔴"            # Rojo = peligroso
    else:                              # Rango 5: Muy dañino
        nivel = "MUY DAÑINA 🟣"        # Morado = emergencia
    
    print(f"📋 Calidad del aire: {nivel}")  # Muestra clasificación con emoji
    
    # CALCULAR TENDENCIA (comparar hoy vs mañana)
    change = predicted_pm25 - real_last_value  # Diferencia: positivo = empeora, negativo = mejora
    if abs(change) < 2:                # Si el cambio es menor a 2 μg/m³
        trend = "ESTABLE ➡️"            # Flecha horizontal = sin cambios significativos
    elif change > 0:                   # Si el cambio es positivo (aumenta)
        trend = f"EMPEORANDO ⬆️ (+{change:.1f})"  # Flecha arriba + cantidad
    else:                              # Si el cambio es negativo (disminuye)
        trend = f"MEJORANDO ⬇️ ({change:.1f})"    # Flecha abajo + cantidad (ya tiene signo -)
    
    print(f"📈 Tendencia: {trend}")      # Muestra tendencia con flecha
    
    # FINALIZACIÓN DEL PROGRAMA
    print("\n" + "="*50)              # Línea separadora
    print("✅ Predicción completada!")    # Mensaje de éxito
    
if __name__ == '__main__':             # Si este archivo se ejecuta directamente (no se importa)
    main()                             # Llama a la función principal
