import plotly.express as px
import plotly.graph_objs as go
from config import datenbank, sensebox
from neuralprophet import NeuralProphet
import sqlalchemy
import requests
import pandas as pd
from datetime import datetime, timedelta

def get_data_from_postgres():
    """
    Stellt Verbindung zur Datenbank her, ladet und verarbeitet die Daten
    
    Returns:
        DataFrame mit den interpolierten Daten
    """

    # SQLAlchemy engine erstellen
    engine = sqlalchemy.create_engine(f"postgresql://{datenbank.USER}:{datenbank.PASSWORD}@{datenbank.HOSTNAME}:{datenbank.PORT}/{datenbank.DBNAME}")
    try:
        sql_query = "SELECT * FROM sensebox"
        df = pd.read_sql(sql_query, engine)
        df = df.sort_values(by='createdat')
        df = df.set_index('createdat').interpolate(method='time').reset_index()
        return df
    except Exception as e:
        print("Fehler beim Laden der Daten aus der Datenbank:", e)
        return pd.DataFrame() 
    

def neural_prophet_forecast(df, time_column, target_column, yaxis_title, periods=480, freq='min', epochs=40):
    """
    Erstellt eine Vorhersage auf Basis historischer Daten und visualisiert sie

    Parameters:
        df: DataFrame mit historischen Daten
        time_column (str): Spaltenname der Zeitdaten
        target_column (str): Spaltenname des Labels
        yaxis_title (str): Titel der y-Achse im Plot
        periods (int, optional): Anzahl der vorherzusagenden Zeitpunkte, Standard ist 480
        freq (str, optional): Frequenz der Zeitdaten, Standard ist min
        epochs (int, optional): Anzahl der Trainingsdurchläufe für das Modell, Standard ist 40

    Returns:
        Plotly-Objekt, das die historischen Daten und die Vorhersage anzeigt
    """

    data = df[[time_column, target_column]]  
    data.columns = ['ds', 'y']  
    
    # NeuralProphet model
    m = NeuralProphet(batch_size = 254, weekly_seasonality=True)
    m.fit(data, freq=freq, epochs=epochs)  
    
    future = m.make_future_dataframe(data, periods=periods)  
    forecast = m.predict(future)
    
    fig = go.Figure()
    
    # Visualierisung historische Daten
    fig.add_trace(go.Scatter(x=data['ds'], y=data['y'], mode='lines', name='Historical Data'))
    
    # Visualisierung Vorhersage
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat1'], mode='lines', name='Forecast'))
    
    fig.update_layout(title=f'Historical and Forecast of {yaxis_title}',
                      xaxis_title='Time',
                      yaxis_title=yaxis_title)
    
    # Vorhersage in rot
    fig.add_shape(
        type="rect",
        xref="x",
        yref="paper",
        x0=forecast['ds'].iloc[0],  # Anfangsdatum der Vorhersage
        y0=0,
        x1=forecast['ds'].iloc[-1],  # Enddatum der Vorhersage
        y1=1,
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0,
    )
    
    # Historische Daten in blau
    fig.add_shape(
        type="rect",
        xref="x",
        yref="paper",
        x0=data['ds'].iloc[0],  # Anfangsdatum der Daten
        y0=0,
        x1=data['ds'].iloc[-1],  # Enddatum der Daten
        y1=1,
        fillcolor="blue",
        opacity=0.2,
        layer="below",
        line_width=0,
    )

    # Beschriftung 
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.2,
        y=0.05,
        text="Historical Data (Blue)",
        showarrow=False,
        font=dict(
            size=12,
            color="black"
        ),
    )
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x= 1,
        y=0.05,
        text="Forecast (Red)",
        showarrow=False,
        font=dict(
            size=12,
            color="black"
        ),
    )

    last_72_hours = datetime.now() - timedelta(hours=72)

    # x-Achse auf den Bereich der letzten 72 Stunden beschränkt
    fig.update_xaxes(range=[last_72_hours, forecast['ds'].iloc[-1]])
    return fig


def create_figure(df, x, y, title, y_title, y2=None, second_y_title=None):
    """
    Erstellt eine Plotly-Liniengrafik mit 1-2 Y-Achsen

    Parameters:
        df: DataFrame mit den Daten zur Darstellung
        x (str): Spaltenname für die x-Achse
        y (str): Spaltenname für die y-Achse
        title (str): Titel der Grafik
        y_title (str): Titel der y-Achse
        y2 (str, optional): Spaltenname für die zweite y-Achse, Standard ist None
        second_y_title (str, optional): Titel der zweiten y-Achse, Standard ist None

    Returns:
       Plotly-Objekt, das die erstellte Liniengrafik darstellt
    """
     
    fig = px.line(df, x=x, y=y, title=title)
    fig.update_traces(line=dict(color='blue'), yaxis='y', name=y, showlegend=True)
    fig.update_layout(
        xaxis=dict(title='Messzeitpunkte', tickangle=45, tickformat='%Y-%m-%d %H:%M', showgrid=True, gridwidth=1, gridcolor='LightGrey'),
        yaxis=dict(title=y_title, showgrid=True, gridwidth=1, gridcolor='LightGrey')
    )
    if y2:
        fig.add_trace(go.Scatter(x=df[x], y=df[y2], mode='lines', name=second_y_title, line=dict(color='red'), yaxis='y2', showlegend=True))

    fig.update_layout(yaxis2=dict(title=second_y_title, overlaying='y', side='right') if second_y_title else {})
    fig.update_layout(annotations=[dict(xref='paper', yref='paper', x=0.5, y=0.0, showarrow=False, text="Hinweis: Ausreißer wurden entfernt und interpoliert")])
    return fig


def correlation_heatmap(df):
    """
    Erstellt eine Heatmap, die die Korrelationen zwischen den numerischen Variablen eines DataFrame zeigt

    Parameters:
        df: DataFrame mit den Daten zur Analyse

    Returns:
        Plotly-Objekt, das die Korrelations-Heatmap darstellt
    """
    df = df.drop(columns="createdat").corr()
    fig = go.Figure(data=go.Heatmap(z=df, x=df.columns, y=df.columns, colorscale='RdBu_r'))
    fig.update_layout(title="Korrelationsmatrix", xaxis_title="Variablen", yaxis_title="Variablen")
    return fig


def get_last_measurement(sensor_id):
    """
    Funktion zum Abrufen der letzten Messung eines Sensors von der Sensebox-API

    Parameters:
        sensor_id (str): Die ID des Sensors

    Returns:
        float or None: Der Wert der letzten Messung des Sensors, oder None im Fehlerfall
    """
    sensor_url = f"{sensebox.BASE_URL}/{sensebox.SENSEBOX_ID}/sensors/{sensor_id}"
    response = requests.get(sensor_url)
    if response.status_code == 200:
        sensor_data = response.json()
        last_measurement = sensor_data.get('lastMeasurement', {})
        return last_measurement.get('value')
    else:
        print(f"Fehler bei der Abfrage des Sensors {sensor_id}: {response.status_code}")
        return None


def create_last_measurement_data():
    """
    Erstellt einen DataFrame mit den letzten Messwerten der Sensoren

    Returns:
        DataFrame mit Spalten 'Sensor', 'Wert' und 'Einheit'
    """
    data = {'Sensor': [], 'Wert': [], 'Einheit': []}
    for sensor_id, sensor_info in sensebox.SENSOR_INFO.items():
        last_value = get_last_measurement(sensor_id)
        if last_value is not None:
            data['Sensor'].append(sensor_info['name'])
            data['Wert'].append(last_value)
            data['Einheit'].append(sensor_info['unit'])
    df = pd.DataFrame(data)
    return df