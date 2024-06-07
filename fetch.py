import requests
import pandas as pd
from config import sensebox, datenbank
import procesing
from datetime import datetime
import psycopg2
from tqdm import tqdm

def get_latest_timestamp():
    """Retrieve the latest timestamp from the database."""
    try:
        conn = psycopg2.connect(
            host=datenbank.HOSTNAME,
            dbname=datenbank.DBNAME,
            user=datenbank.USER,
            password=datenbank.PASSWORD,
            port=datenbank.PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT MAX(createdAt) FROM sensebox;")
        latest_timestamp = cur.fetchone()[0]
        cur.close()
        conn.close()
        return latest_timestamp
    except Exception as error:
        print("Error retrieving latest timestamp:", error)
        return None


def fetch_sensebox_data(from_date=None):
    conn = psycopg2.connect(
            host=datenbank.HOSTNAME,
            dbname=datenbank.DBNAME,
            user=datenbank.USER,
            password=datenbank.PASSWORD,
            port=datenbank.PORT
        )
    cur = conn.cursor()
    cur.execute("SELECT MAX(createdAt) FROM sensebox;")
    latest_timestamp = cur.fetchone()[0]
    cur.close()
    conn.close() 
    PARAMS = {
        'format': 'json',
        'download': 'true',
        'outliers': 'mark',
        'outlier-window': 15,
    }
    if from_date:
        PARAMS['from-date'] = from_date
        
    all_data = []
    print("requesting new data...")
    for sensorId in sensebox.SENSOR_INFO.keys():
        endpoint = f'{sensebox.BASE_URL}/{sensebox.SENSEBOX_ID}/data/{sensorId}'
        response = requests.get(endpoint, params=PARAMS)
        
        if response.status_code == 200:
            data = response.json()
            for measurement in data:
                measurement['Id'] = sensorId
                if 'outlier' in measurement:
                    measurement['outlier'] = measurement['outlier']
                else:
                    measurement['outlier'] = None
            all_data.extend(data)
        else:
            print(f'Error retrieving data for sensor {sensorId}: {response.status_code}')

    sense_df = pd.DataFrame(all_data)
    return sense_df


# Zur Sicherheit die Daten als CSV speichern
def export_to_csv(df):
    print("exporting to csv...")
    df.to_csv(f"data/sensor_data_{datetime.now().date()}.csv")


def update_db(df):
    try:
        print("updating db table...")
        conn = psycopg2.connect(
            host= datenbank.HOSTNAME,
            dbname= datenbank.DBNAME,
            user= datenbank.USER,
            password= datenbank.PASSWORD,
            port= datenbank.PORT
        )

        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS sensebox (
                createdAt TIMESTAMPTZ PRIMARY KEY,
                Luftdruck FLOAT,
                Temperatur FLOAT,
                UVIntensität FLOAT,
                relLuftfeuchte FLOAT
            );
            """)
        conn.commit()

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="updating rows"):
            sql = """
            INSERT INTO sensebox (createdAt, Luftdruck, Temperatur, UVIntensität, relLuftfeuchte)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (createdAt) DO UPDATE
            SET Luftdruck = EXCLUDED.Luftdruck,
                Temperatur = EXCLUDED.Temperatur,
                UVIntensität = EXCLUDED.UVIntensität,
                relLuftfeuchte = EXCLUDED.relLuftfeuchte;
            """
            values = (pd.to_datetime(row["createdAt"]).strftime('%Y-%m-%d %H:%M'),\
                      row['Luftdruck'], row['Temperatur'], row['UV-Intensität'], row['rel. Luftfeuchte'])
            cur.execute(sql, values)

        conn.commit()
        cur.close()
        conn.close()
        print("update was successful")

    except Exception as error:
        print("update failed:", error)


if __name__ == "__main__":
    from_date = datetime.fromisoformat(str(get_latest_timestamp())).strftime('%Y-%m-%dT%H:%M:%SZ')
    # data = fetch_sensebox_data(from_date=from_date)
    # export_to_csv(data)
    data = pd.read_csv('/Users/rafaelriesle/Downloads/Umweltmonitoring/data/sensor_data_2024-05-27.csv')
    update_db(procesing.clean_data(data))

