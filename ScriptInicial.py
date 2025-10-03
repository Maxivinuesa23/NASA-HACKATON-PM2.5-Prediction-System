import torch
from torch.utils.data import DataLoader, random_split
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Importar funciones y clases del proyecto
from SimuladorCalidadAire import generate_openaq_data, generate_synthetic_data, AirQualityDataset, SEQ_LENGTH, N_FEATURES, SCALER, today, tomorrow, select_city
from ModeloLSTM import AirQualityPredictor, train_model, make_single_prediction, HIDDEN_DIM, NUM_LAYERS, OUTPUT_DIM, BATCH_SIZE, DROPOUT_RATE

# Ruta para guardar/cargar el modelo
MODEL_PATH = 'air_quality_predictor_model.pth'

def plot_training_history(history):
    """
    Grafica la pérdida de entrenamiento y validación.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(history['train_loss'], label='Pérdida Entrenamiento (MSE)', color='skyblue')
    plt.plot(history['val_loss'], label='Pérdida Validación (MSE)', color='tomato')
    plt.title('Historial de Pérdida del Modelo (Error Cuadrático Medio)')
    plt.xlabel('Época')
    plt.ylabel('Pérdida (MSE)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_predictions(targets_scaled, predictions_scaled, title="Predicciones vs. Reales (Conjunto de Validación)"):
    """
    Grafica las predicciones del modelo frente a los valores reales DESNORMALIZADOS.
    """
    # Importar el SCALER desde el módulo
    from SimuladorCalidadAire import SCALER
    
    # Desnormalizar manualmente usando mean y scale para la columna PM2.5 (índice 1)
    mean_pm25 = SCALER.mean_[1]
    scale_pm25 = SCALER.scale_[1]
    
    targets = (targets_scaled * scale_pm25) + mean_pm25
    predictions = (predictions_scaled * scale_pm25) + mean_pm25
    
    
    plt.figure(figsize=(12, 6))
    plt.plot(targets, label='Valores Reales (PM2.5)', color='darkgreen', linewidth=2)
    plt.plot(predictions, label='Predicciones del Modelo', color='orange', linestyle='--', alpha=0.7)
    
    plt.title(title)
    plt.xlabel('Muestra (Día)')
    plt.ylabel('Concentración de PM2.5 ($\\mu g/m^3$)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.show()


def main():
    """
    Flujo principal de la aplicación: prepara datos, entrena y realiza una predicción.
    """
    
    print("🤖 PREDICTOR DE CALIDAD DEL AIRE")
    print("="*50)
    print(f"📅 Fecha actual: {today}")
    print(f"🔮 Predicción para: {tomorrow}")
    print("="*50)
    
    # Selección de ciudad
    selected_city = select_city()
    
    # 1. Preparación de Datos
    print("\n📊 Obteniendo datos...")
    raw_data_scaled = generate_openaq_data(selected_city)
    
    if raw_data_scaled is None or len(raw_data_scaled) < SEQ_LENGTH + 50:
        print("⚠️  Usando datos sintéticos como respaldo...")
        raw_data_scaled = generate_synthetic_data(selected_city)
    else:
        print("✅ Datos reales de OpenAQ obtenidos exitosamente!")
    
    full_dataset = AirQualityDataset(raw_data_scaled, SEQ_LENGTH)
    
    # Dividir el dataset para entrenamiento y validación (80% / 20%)
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    # Crear DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    print(f"📈 Entrenamiento: {len(train_dataset)} secuencias")
    print(f"📊 Validación: {len(val_dataset)} secuencias")
    
    # 2. Modelo
    print("\n🧠 Preparando modelo LSTM...")
    model = AirQualityPredictor(N_FEATURES, HIDDEN_DIM, NUM_LAYERS, OUTPUT_DIM, DROPOUT_RATE)
    
    try:
        # Intenta cargar un modelo pre-entrenado
        model.load_state_dict(torch.load(MODEL_PATH))
        print("✅ Modelo cargado desde archivo")
    except FileNotFoundError:
        print("🔄 Entrenando nuevo modelo...")
        train_model(model, train_loader, val_loader)
        
        # Guardar el modelo entrenado
        torch.save(model.state_dict(), MODEL_PATH)
        print("💾 Modelo guardado")

    # 3. Predicción para MAÑANA
    print(f"\n🔮 PREDICCIÓN PARA {selected_city['name'].upper()} - {tomorrow}")
    print("-"*50)
    
    # Usar la última secuencia disponible (datos hasta HOY)
    # Acceder directamente a los datos del dataset
    last_sequence_data, _ = full_dataset[len(full_dataset)-1]
    prediction_sequence = last_sequence_data.cpu().numpy()
    
    # Obtener el valor real del último día para referencia
    from SimuladorCalidadAire import SCALER
    if SCALER is not None:
        # Usar los datos originales para obtener el último valor real
        last_pm25_scaled = full_dataset.data[-1][1].item()  # PM2.5 está en índice 1
        mean_pm25 = SCALER.mean_[1]
        scale_pm25 = SCALER.scale_[1]
        real_last_value = (last_pm25_scaled * scale_pm25) + mean_pm25
    else:
        real_last_value = 25.0  # Valor por defecto
    
    # Predicción para MAÑANA
    predicted_pm25 = make_single_prediction(model, prediction_sequence)
    
    print(f"📊 PM2.5 actual (hoy): {real_last_value:.1f} μg/m³")
    print(f"🎯 PM2.5 predicho (mañana): {predicted_pm25:.1f} μg/m³")
    
    # Interpretación
    if predicted_pm25 <= 12:
        nivel = "BUENA 🟢"
    elif predicted_pm25 <= 35:
        nivel = "MODERADA 🟡"  
    elif predicted_pm25 <= 55:
        nivel = "DAÑINA GRUPOS SENSIBLES 🟠"
    elif predicted_pm25 <= 150:
        nivel = "DAÑINA 🔴"
    else:
        nivel = "MUY DAÑINA 🟣"
    
    print(f"📋 Calidad del aire: {nivel}")
    
    # Tendencia
    change = predicted_pm25 - real_last_value
    if abs(change) < 2:
        trend = "ESTABLE ➡️"
    elif change > 0:
        trend = f"EMPEORANDO ⬆️ (+{change:.1f})"
    else:
        trend = f"MEJORANDO ⬇️ ({change:.1f})"
    
    print(f"📈 Tendencia: {trend}")
    print("\n" + "="*50)
    print("✅ Predicción completada!")
    
if __name__ == '__main__':
    main()
