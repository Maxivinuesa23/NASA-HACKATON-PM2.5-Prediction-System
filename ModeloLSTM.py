# ========================================
# MODELO LSTM PARA PREDICCIÓN DE CALIDAD DEL AIRE
# Red neuronal que aprende patrones temporales de contaminación
# ========================================

# IMPORTACIONES DE MACHINE LEARNING
import torch                           # Framework principal de machine learning
import torch.nn as nn                  # Módulo de redes neuronales (capas, funciones)
from torch.utils.data import DataLoader, random_split  # Para cargar y dividir datos
import numpy as np                     # Para operaciones matemáticas

# IMPORTAR CONFIGURACIÓN DESDE NUESTRO SIMULADOR
from AirVisualSimulator import SEQ_LENGTH, N_FEATURES, SCALER  # Parámetros globales del sistema

# ========================================
# CONFIGURACIÓN DEL MODELO LSTM
# Parámetros que definen la arquitectura y entrenamiento
# ========================================
HIDDEN_DIM = 64                        # Neuronas en capas ocultas (memoria del modelo)
NUM_LAYERS = 2                         # Número de capas LSTM apiladas (profundidad)
OUTPUT_DIM = 1                         # Salidas del modelo (solo PM2.5)
LEARNING_RATE = 0.001                  # Velocidad de aprendizaje (qué tan rápido aprende)
N_EPOCHS = 30                          # Ciclos completos de entrenamiento
BATCH_SIZE = 32                        # Ejemplos procesados simultáneamente
DROPOUT_RATE = 0.2                     # Porcentaje de neuronas "apagadas" para evitar sobreajuste

# CONFIGURAR DISPOSITIVO DE CÓMPUTO
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # GPU si está disponible, sino CPU
print(f"Usando dispositivo: {DEVICE}")  # Informa al usuario qué está usando

class AirQualityPredictor(nn.Module):
    """
    CLASE: Modelo de red neuronal LSTM para predecir calidad del aire
    PROPÓSITO: Aprender patrones temporales en datos de contaminación
    ARQUITECTURA: Entrada → LSTM → Capa densa → Salida (PM2.5)
    """
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim, dropout_rate):
        """
        CONSTRUCTOR: Inicializa la arquitectura del modelo
        PARÁMETROS: Dimensiones de entrada, oculta, salida, y configuración
        """
        super(AirQualityPredictor, self).__init__()  # Llama constructor de la clase padre
        
        # GUARDAR PARÁMETROS
        self.hidden_dim = hidden_dim       # Tamaño de memoria interna
        self.num_layers = num_layers       # Número de capas LSTM
        
        # CREAR CAPA LSTM
        self.lstm = nn.LSTM(               # Long Short-Term Memory (memoria a largo plazo)
            input_size=input_dim,          # Entrada: 2 características (PM2.5, NO2)
            hidden_size=hidden_dim,        # Memoria interna: 64 neuronas
            num_layers=num_layers,         # Profundidad: 2 capas apiladas
            batch_first=True,              # Formato: (batch, secuencia, características)
            dropout=dropout_rate           # Dropout: apaga 20% de neuronas aleatoriamente
        ).to(DEVICE)                       # Mover a GPU/CPU
        
        # CREAR CAPA DE SALIDA (DENSA/LINEAL)
        self.fc = nn.Linear(hidden_dim, output_dim).to(DEVICE)  # 64 neuronas → 1 salida (PM2.5)

    def forward(self, x):
        """
        MÉTODO: Define cómo fluyen los datos a través del modelo
        PARÁMETRO: x (secuencias de entrada de 10 días)
        RETORNA: Predicción de PM2.5 para el día siguiente
        """
        # INICIALIZAR ESTADOS OCULTOS DEL LSTM (memoria inicial = zeros)
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(DEVICE)  # Estado oculto inicial
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(DEVICE)  # Estado de celda inicial
        
        # PASAR DATOS POR LSTM
        out, _ = self.lstm(x, (h0, c0))    # LSTM procesa secuencia completa, devuelve salidas de todos los pasos
        
        # USAR SOLO LA ÚLTIMA SALIDA DEL LSTM (último día de la secuencia)
        out = self.fc(out[:, -1, :])       # Capa lineal: 64 dimensiones → 1 predicción
        
        return out                         # Devuelve predicción de PM2.5

def train_model(model, train_loader, val_loader):
    """
    FUNCIÓN: Entrena el modelo LSTM con los datos
    PROPÓSITO: Enseñar al modelo a reconocer patrones temporales
    PARÁMETROS: model (modelo a entrenar), train_loader (datos entrenamiento), val_loader (datos validación)
    """
    # CONFIGURAR ENTRENAMIENTO
    criterion = nn.MSELoss()               # Función de pérdida: Error Cuadrático Medio
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)  # Optimizador Adam
    
    history = {'train_loss': [], 'val_loss': []}  # Historial de pérdidas para graficar
    
    print("\n--- INICIANDO ENTRENAMIENTO ---")
    
    # CICLO PRINCIPAL DE ENTRENAMIENTO
    for epoch in range(N_EPOCHS):         # Repite 30 veces (épocas)
        model.train()                      # Modo entrenamiento (activa dropout)
        train_loss = 0                     # Acumulador de pérdida de entrenamiento
        
        # PROCESAR CADA LOTE DE DATOS
        for X_batch, y_batch in train_loader:  # X_batch = secuencias, y_batch = valores objetivo
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)  # Mover a GPU/CPU
            
            # PASO HACIA ADELANTE (FORWARD)
            y_pred = model(X_batch)        # Obtener predicciones del modelo
            loss = criterion(y_pred, y_batch)  # Calcular error entre predicción y realidad
            
            # PASO HACIA ATRÁS (BACKWARD) - APRENDIZAJE
            optimizer.zero_grad()          # Limpiar gradientes anteriores
            loss.backward()                # Calcular gradientes (derivadas)
            optimizer.step()               # Actualizar pesos del modelo
            
            # ACUMULAR PÉRDIDA
            train_loss += loss.item() * X_batch.size(0)  # Sumar pérdida ponderada por tamaño del lote
            
        # CALCULAR PÉRDIDA PROMEDIO DE LA ÉPOCA
        train_loss /= len(train_loader.dataset)  # Dividir por número total de ejemplos
        
        # EVALUAR EN DATOS DE VALIDACIÓN
        val_loss = evaluate_model(model, val_loader, criterion)  # Probar modelo en datos no vistos
        
        # GUARDAR HISTORIAL
        history['train_loss'].append(train_loss)  # Guardar pérdida de entrenamiento
        history['val_loss'].append(val_loss)      # Guardar pérdida de validación
        
        # MOSTRAR PROGRESO
        print(f"Epoch [{epoch+1}/{N_EPOCHS}], Pérdida Entrenamiento: {train_loss:.4f}, Pérdida Validación (MSE): {val_loss:.4f}")

    print("--- ENTRENAMIENTO FINALIZADO ---")
    return history                         # Devolver historial para graficar

def evaluate_model(model, data_loader, criterion):
    """
    FUNCIÓN: Evalúa el rendimiento del modelo en un conjunto de datos
    PROPÓSITO: Medir qué tan bien predice el modelo sin entrenar
    RETORNA: Pérdida promedio en el conjunto de datos
    """
    model.eval()                           # Modo evaluación (desactiva dropout)
    total_loss = 0                         # Acumulador de pérdida total
    
    with torch.no_grad():                  # No calcular gradientes (ahorra memoria y tiempo)
        for X_batch, y_batch in data_loader:  # Procesar cada lote
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)  # Mover a dispositivo
            y_pred = model(X_batch)        # Obtener predicciones
            loss = criterion(y_pred, y_batch)  # Calcular error
            total_loss += loss.item() * X_batch.size(0)  # Acumular pérdida
            
    return total_loss / len(data_loader.dataset)  # Devolver pérdida promedio

def get_predictions_and_targets(model, data_loader):
    """
    FUNCIÓN: Obtiene todas las predicciones y valores reales para comparar
    PROPÓSITO: Generar datos para gráficos de comparación
    RETORNA: Arrays de predicciones y valores reales
    """
    model.eval()                           # Modo evaluación
    predictions = []                       # Lista para predicciones
    targets = []                           # Lista para valores reales
    
    with torch.no_grad():                  # Sin gradientes
        for X_batch, y_batch in data_loader:  # Procesar cada lote
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)  # Mover a dispositivo
            y_pred = model(X_batch)        # Obtener predicciones
            
            # CONVERTIR A LISTAS DE PYTHON
            predictions.extend(y_pred.cpu().numpy().flatten())  # Agregar predicciones
            targets.extend(y_batch.cpu().numpy().flatten())     # Agregar valores reales
            
    return np.array(predictions), np.array(targets)  # Convertir a arrays de NumPy


def make_single_prediction(model, sequence):
    """
    FUNCIÓN: Realiza una predicción para un solo día usando secuencia de 10 días
    PROPÓSITO: Predecir PM2.5 de mañana basado en últimos 10 días
    PARÁMETRO: sequence (array de 10 días × 2 características)
    RETORNA: Valor de PM2.5 predicho en μg/m³ (desnormalizado)
    """
    model.eval()                           # Modo evaluación
    with torch.no_grad():                  # Sin gradientes
        # PASO 1: PREPARAR DATOS
        sequence_tensor = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0).to(DEVICE)
        # ↑ Convierte array → tensor, agrega dimensión de lote, mueve a dispositivo
        
        # PASO 2: OBTENER PREDICCIÓN (NORMALIZADA 0-1)
        prediction_scaled = model(sequence_tensor).cpu().numpy().flatten()[0]
        # ↑ Pasa por modelo, mueve a CPU, convierte a array, toma primer elemento
        
        # PASO 3: DESNORMALIZAR LA PREDICCIÓN (convertir 0-1 → μg/m³)
        from AirVisualSimulator import SCALER  # Importar objeto normalizador
        
        # OBTENER PARÁMETROS DE NORMALIZACIÓN
        mean = SCALER.mean_[0]             # Media usada para normalizar PM2.5 (columna 0)
        scale = SCALER.scale_[0]           # Escala usada para normalizar PM2.5
        
        # FÓRMULA DE DESNORMALIZACIÓN: valor_real = (valor_normalizado × escala) + media
        predicted_unscaled = (prediction_scaled * scale) + mean
        
        return predicted_unscaled          # Devuelve predicción en μg/m³
