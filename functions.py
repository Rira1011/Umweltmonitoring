import plotly.express as px
import plotly.graph_objs as go
from config import datenbank
from neuralprophet import NeuralProphet
import sqlalchemy
import pandas as pd
from datetime import datetime, timedelta



# Verbindung zur Datenbank herstellen und Daten laden
def get_data_from_postgres():
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
    

#Forcasting  
def neural_prophet_forecast(df, time_column, target_column, yaxis_title, periods=480, freq='min', epochs=40):
    data = df[[time_column, target_column]]  
    data.columns = ['ds', 'y']  
    
    # NeuralProphet model
    m = NeuralProphet(batch_size = 254, weekly_seasonality=True)
    m.fit(data, freq=freq, epochs=epochs)  
    
    # dataframe for forecasting
    future = m.make_future_dataframe(data, periods=periods)  
    
    # predictions
    forecast = m.predict(future)
    
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(x=data['ds'], y=data['y'], mode='lines', name='Historical Data'))
    
    # Forecast
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat1'], mode='lines', name='Forecast'))
    
    fig.update_layout(title=f'Historical and Forecast of {yaxis_title}',
                      xaxis_title='Time',
                      yaxis_title=yaxis_title)
    
    # Markierung für den Vorhersagehintergrund (rot)
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
    
    # Markierung für den historischen Bereich (blau)
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

    # Beschriftung für den historischen und Vorhersagebereich
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
    # Berechne den Startzeitpunkt für die Anzeige der letzten 72 Stunden
    last_72_hours = datetime.now() - timedelta(hours=72)

    # Hier wird die x-Achse auf den Bereich der letzten 24 Stunden beschränkt
    fig.update_xaxes(range=[last_72_hours, forecast['ds'].iloc[-1]])
    return fig

# Funktion zum Erstellen eines Diagramms
def create_figure(df, x, y, title, y_title, y2=None, second_y_title=None):
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

# Funktion zum Erstellen einer Korrelations-Heatmap
def correlation_heatmap(df):
    df = df.drop(columns="createdat").corr()
    fig = go.Figure(data=go.Heatmap(z=df, x=df.columns, y=df.columns, colorscale='RdBu_r'))
    fig.update_layout(title="Korrelationsmatrix", xaxis_title="Variablen", yaxis_title="Variablen")
    return fig