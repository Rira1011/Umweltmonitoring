import fetch
from config import sensebox
import pandas as pd


def clean_data(sense_df):
    """
    Bereinigt die Rohdaten der Sensebox und strukturiert sie 

    Parameters:
        sense_df: DataFrame mit den Rohdaten von der Sensebox

    Returns:
        Bereinigter und strukturierter DataFrame
    """
    print("processing data...")
    sense_df['createdAt'] = pd.to_datetime(sense_df['createdAt'])
    sense_df['sensor_name'] = sense_df['Id'].map(lambda x: sensebox.SENSOR_INFO[x]['name'])
    sense_df['unit'] = sense_df['Id'].map(lambda x: sensebox.SENSOR_INFO[x]['unit']) # Einheit hinzufügen 
    
    df = sense_df[sense_df['isOutlier'] == False] # Filtert Ausreißer und konvertiert Werte
    df.loc[:, 'value'] = pd.to_numeric(df['value'], errors='coerce')
    
    opensense_df = df.pivot_table(index='createdAt', columns='sensor_name', values='value').reset_index()
    
    opensense_df.attrs["num_measurments"] = len(sense_df)
    opensense_df.attrs["num_outliers"] = sense_df['isOutlier'].sum()
    opensense_df.attrs["percent_outliers"] = round((sense_df['isOutlier'].sum() / len(sense_df)) * 100, 2)
    
    return opensense_df


if __name__ == "__main__":
    sense_df = fetch.fetch_sensebox_data()
    clean_data(sense_df)