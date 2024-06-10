# Umweltmonitoring-Projekt

Dieses Projekt dient zur Überwachung von Umweltparametern mithilfe einer SenseBox und bietet Funktionen zur Datenverarbeitung, Visualisierung und Analyse.

## Dateien

- **Processing**: Python-Skript zur Verarbeitung der Sensor-Daten. Es enthält Funktionen zum Bereinigen und Aufbereiten der Daten für die Analyse.

- **Functions**: Enthält verschiedene Funktionen zur Datenanalyse und Visualisierung, wie z.B. zur Vorhersage von Umweltparametern mithilfe von neuronalen Propheten und zur Erstellung von Diagrammen.

- **Fetch**: Skript zum Abrufen von Daten von der SenseBox und Aktualisieren der Datenbank. Es enthält Funktionen zum Herunterladen von Daten, Exportieren in CSV-Dateien und Aktualisieren der Datenbank.

- **Config**: Konfigurationsdatei für die Projektparameter, wie z.B. URLs, Sensorkonfigurationen und Datenbankinformationen.

- **App**: Dash-Anwendung zur Benutzeroberfläche. Enthält Seiten für die Datenvisualisierung und -analyse sowie eine Schnittstelle zum Aktualisieren der Datenbank und Sensordaten.

- **Modell**: Seite der Dash-Anwendung zur Vorhersageanalyse mithilfe neuronaler Propheten.

- **Analysis**: Seite der Dash-Anwendung zur Datenanalyse, einschließlich Zeitreihenanalyse und Korrelationsanalyse.

## Nutzung

1. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind, indem Sie `pip install -r requirements.txt` ausführen.

2. Konfigurieren Sie die Parameter in der `config.py`-Datei entsprechend Ihren Anforderungen.

3. Führen Sie das `app.py`-Skript aus, um die Dash-Anwendung zu starten und auf die Benutzeroberfläche zuzugreifen.

4. Verwenden Sie die Dash-Anwendung, um Daten herunterzuladen, zu visualisieren und zu analysieren, sowie die Datenbank und Sensordaten zu aktualisieren.

## Abhängigkeiten

- Plotly: Für interaktive Diagramme und Visualisierungen.
- Dash: Für die Entwicklung von Webanwendungen.
- Pandas: Für die Datenmanipulation und -analyse.
- SQLAlchemy: Zur Interaktion mit der Datenbank.
- psycopg2: Für die PostgreSQL-Datenbankverbindung.
- NeuralProphet: Für die Vorhersageanalyse mit neuronalen Propheten.
- Dash Bootstrap Components: Für das Layout und das Styling der Dash-Anwendung.

