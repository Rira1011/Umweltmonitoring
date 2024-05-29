import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, Dataset
from procesing import opensense_df


# Nur die Temperaturspalte verwenden und NaN-Werte entfernen
temperature_data = opensense_df[['createdAt', 'Temperatur']].dropna()

# Konvertiere createdAt zu datetime und setze es als Index
temperature_data['createdAt'] = pd.to_datetime(temperature_data['createdAt'])
temperature_data.set_index('createdAt', inplace=True)

# Skaliere die Daten
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(temperature_data)

# Konvertiere die skalierten Daten zurück zu einem DataFrame
scaled_data = pd.DataFrame(scaled_data, index=temperature_data.index, columns=['Temperatur'])




# Dataset Klasse
class TimeSeriesDataset(Dataset):
    def __init__(self, data, seq_length):
        self.data = data
        self.seq_length = seq_length

    def __len__(self):
        return len(self.data) - self.seq_length

    def __getitem__(self, index):
        x = self.data[index:index + self.seq_length]
        y = self.data[index + self.seq_length]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

sequence_length = 50  # Länge der Eingabesequenz
dataset = TimeSeriesDataset(scaled_data.values, sequence_length)

# Aufteilen in Trainings- und Testdaten
train_size = int(len(dataset) * 0.8)
test_size = len(dataset) - train_size

train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)




# LSTM Modell Klasse
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_layer_size, output_size):
        super(LSTMModel, self).__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size)
        self.linear = nn.Linear(hidden_layer_size, output_size)
        self.hidden_cell = (torch.zeros(1, 1, self.hidden_layer_size),
                            torch.zeros(1, 1, self.hidden_layer_size))

    def forward(self, input_seq):
        lstm_out, self.hidden_cell = self.lstm(input_seq.view(len(input_seq), 1, -1), self.hidden_cell)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        return predictions[-1]

input_size = 50
hidden_layer_size = 50
output_size = 1

model = LSTMModel(input_size, hidden_layer_size, output_size)



# Trainingsprozess
loss_function = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.00001)

epochs = 20

for epoch in range(epochs):
    for seq, labels in train_loader:
        optimizer.zero_grad()
        model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size),
                             torch.zeros(1, 1, model.hidden_layer_size))

        y_pred = model(seq)

        single_loss = loss_function(y_pred, labels)
        single_loss.backward()
        optimizer.step()

    if epoch % 1 == 0:
        print(f'epoch: {epoch:3} loss: {single_loss.item():10.8f}')

print(f'epoch: {epoch:3} loss: {single_loss.item():10.10f}')

# Modell testen
test_losses = []
with torch.no_grad():
    for seq, labels in test_loader:
        y_pred = model(seq)
        single_loss = loss_function(y_pred, labels)
        test_losses.append(single_loss.item())

print(f'Test loss: {np.mean(test_losses):10.10f}')


# Setze das Modell in den Evaluierungsmodus
model.eval()

# Verwende die letzten sequence_length Datenpunkte, um die Vorhersage für den nächsten Tag zu machen
last_sequence = scaled_data.values[-sequence_length:]
last_sequence = torch.tensor(last_sequence, dtype=torch.float32).unsqueeze(0)

with torch.no_grad():
    model.hidden_cell = (torch.zeros(1, 1, model.hidden_layer_size),
                         torch.zeros(1, 1, model.hidden_layer_size))
    prediction = model(last_sequence)

# Die skalierte Vorhersage zurück in den ursprünglichen Bereich transformieren
prediction = prediction.numpy()
predicted_temperature = scaler.inverse_transform(prediction.reshape(-1, 1))

print(f'Vorhergesagte Temperatur für den nächsten Tag: {predicted_temperature[0][0]}')