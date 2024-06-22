import psycopg2
import pandas as pd
from config import datenbank
# Verbindung zur Datenbank herstellen
conn = psycopg2.connect(
            host=datenbank.HOSTNAME,
            dbname=datenbank.DBNAME,
            user=datenbank.USER,
            password=datenbank.PASSWORD,
            port=datenbank.PORT
        )

# SQL-Abfrage
sql_query = 'SELECT * FROM sensebox'

# Daten in ein Pandas DataFrame laden
df = pd.read_sql_query(sql_query, conn)

# Daten in eine CSV-Datei exportieren
df.to_csv('data/sensor_data.csv', index=False)

# Verbindung schließen
conn.close()
