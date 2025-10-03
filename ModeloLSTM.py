import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import numpy as np

# Importamos la configuración y el Dataset del simulador
from SimuladorCalidadAire import generate_synthetic_data, AirQualityDataset, SEQ_LENGTH, N_FEATURES, SCALER

# --- CONFIGURACIÓN DEL MODELO ---
HIDDEN_DIM = 64     
NUM_LAYERS = 2      # Aumentamos a 2 capas para mayor capacidad
OUTPUT_DIM = 1      
LEARNING_RATE = 0.001
N_EPOCHS = 30       # Aumentamos las épocas para mejor convergencia
BATCH_SIZE = 32     
DROPOUT_RATE = 0.2  # Tasa de Dropout para prevenir sobreajuste

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {DEVICE}")

class AirQualityPredictor(nn.Module):
    """
    Modelo de Red Neuronal Recurrente (LSTM) con capa de Dropout.
    """
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim, dropout_rate):
        super(AirQualityPredictor, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_dim, 
            hidden_size=hidden_dim, 
            num_layers=num_layers, 
            batch_first=True,
            dropout=dropout_rate # Añadido Dropout para prevenir sobreajuste
        ).to(DEVICE)
        
        self.fc = nn.Linear(hidden_dim, output_dim).to(DEVICE)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(DEVICE)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(DEVICE)
        
        out, _ = self.lstm(x, (h0, c0))
        
        # Tomar la salida de la última secuencia de tiempo
        out = self.fc(out[:, -1, :])
        
        return out

def train_model(model, train_loader, val_loader):
    """
    Bucle de entrenamiento del modelo. Devuelve el historial de pérdidas.
    """
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    history = {'train_loss': [], 'val_loss': []}
    
    print("\n--- INICIANDO ENTRENAMIENTO ---")
    
    for epoch in range(N_EPOCHS):
        model.train()
        train_loss = 0
        
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            
            y_pred = model(X_batch)
            loss = criterion(y_pred, y_batch)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * X_batch.size(0)
            
        train_loss /= len(train_loader.dataset)
        
        # Evaluación en el conjunto de validación
        val_loss = evaluate_model(model, val_loader, criterion)
        
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        
        print(f"Epoch [{epoch+1}/{N_EPOCHS}], Pérdida Entrenamiento: {train_loss:.4f}, Pérdida Validación (MSE): {val_loss:.4f}")

    print("--- ENTRENAMIENTO FINALIZADO ---")
    return history

def evaluate_model(model, data_loader, criterion):
    """
    Evalúa el rendimiento del modelo en un conjunto de datos y devuelve el error.
    """
    model.eval()
    total_loss = 0
    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            y_pred = model(X_batch)
            loss = criterion(y_pred, y_batch)
            total_loss += loss.item() * X_batch.size(0)
            
    return total_loss / len(data_loader.dataset)

def get_predictions_and_targets(model, data_loader):
    """
    Obtiene las predicciones y los valores reales del conjunto de validación.
    """
    model.eval()
    predictions = []
    targets = []
    
    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            y_pred = model(X_batch)
            
            predictions.extend(y_pred.cpu().numpy().flatten())
            targets.extend(y_batch.cpu().numpy().flatten())
            
    return np.array(predictions), np.array(targets)


def make_single_prediction(model, sequence):
    """
    Realiza una predicción sobre una única secuencia de 10 días y la desnormaliza.
    """
    model.eval()
    with torch.no_grad():
        # 1. Convertir y mover a dispositivo
        sequence_tensor = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0).to(DEVICE)
        
        # 2. Obtener predicción (Valor NORMALIZADO)
        prediction_scaled = model(sequence_tensor).cpu().numpy().flatten()[0]
        
        # 3. Desnormalizar la predicción
        # Importar el SCALER desde el módulo
        from SimuladorCalidadAire import SCALER
        
        # La columna 1 (índice 1) es PM2.5_Ground
        mean = SCALER.mean_[1]
        scale = SCALER.scale_[1]
        
        # Fórmula de desnormalización: valor_original = (valor_escalado * desviación_estándar) + media
        predicted_unscaled = (prediction_scaled * scale) + mean
        
        return predicted_unscaled
