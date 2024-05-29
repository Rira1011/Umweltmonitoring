import requests
import pandas as pd
import pandas as pd
from config import sensebox, datenbank
import procesing
from datetime import datetime
import psycopg2
from tqdm import tqdm


def fetch_sensebox_data():
    all_data = []
    print("requesting new data...")
    for sensorId in sensebox.SENSOR_INFO.keys():
        endpoint = f'{sensebox.BASE_URL}/{sensebox.SENSEBOX_ID}/data/{sensorId}'
        response = requests.get(endpoint, params=sensebox.PARAMS)
        
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

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="updating rows"):
            sql = """
            UPDATE sensebox
            SET Luftdruck = %s, Temperatur = %s, UVIntensität = %s, relLuftfeuchte = %s
            WHERE createdAt = %s;
            """
            values = (row['Luftdruck'], row['Temperatur'], row["UV-Intensität"], row["rel. Luftfeuchte"], row['createdAt'])
            cur.execute(sql, values)

        conn.commit()
        cur.close()
        conn.close()
        print("update was sucessful")

    except Exception as error:
        print("update failed:", error)


if __name__ == "__main__":
    data = procesing.clean_data(fetch_sensebox_data())
    export_to_csv(data)
    update_db(data)