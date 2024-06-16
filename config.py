from dataclasses import  dataclass

# definiert zentrale Konfigurationsvariablen für die Anwendung

# Dataclass für sensebox-Konfigurationen
@dataclass(frozen=True)
class sensebox():
    BASE_URL = "https://api.opensensemap.org/boxes"
    SENSEBOX_ID = "6645db6eeb5aad0007a6e4b6"
    SENSOR_INFO = {
        '6645db6eeb5aad0007a6e4b7': {'name': 'Temperatur', 'unit': '°C'},
        '6645db6eeb5aad0007a6e4b8': {'name': 'rel. Luftfeuchte', 'unit': '%'},
        '6645db6eeb5aad0007a6e4b9': {'name': 'Luftdruck', 'unit': 'hPa'},
        '6645db6eeb5aad0007a6e4ba': {'name': 'UV-Intensität', 'unit': 'μW/cm²'},
    }
    PARAMS = {
    'format': 'json',            
    'from-date': '2024-05-16T19:00:00Z',
    'download': 'true',          
    'outliers': 'mark',          
    'outlier-window': 15,        
    }
    STATION_LOCATION = {
    "latitude": 49.001548,
    "longitude": 8.410042,
    }

# Dataclass für Datenbankverbindung
@dataclass(frozen=True)
class datenbank():
    HOSTNAME = '35.192.180.193'
    DBNAME = 'Umweltmonitoring-DB'
    USER = 'postgres'
    PASSWORD = 'mezjaw-8mofja-dyxdIv'
    PORT = 5432