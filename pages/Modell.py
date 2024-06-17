import dash
from dash import dcc, html, callback, Output, Input
from functions import get_data_from_postgres, neural_prophet_forecast
import multiprocessing
import fetch
import procesing

# Dritte Seite des Dashboards: Forecasting-Modell

dash.register_page(__name__, name='Modell')

df = procesing.clean_data(fetch.fetch_sensebox_data())


def process_forecast(df, x_col, y_col, title):
    """
    Erstellt eine Grafik für eine Vorhersage mit Neural Prophet

    Parameters:
    - df (DataFrame): Zeitreihendaten
    - x_col (str): Feature-Spalten
    - y_col (str): Label-Spalte
    - title (str): Titel der Grafik

    Returns:
    - Vorhersage-Grafik
    """

    return dcc.Graph(
        figure=neural_prophet_forecast(df, x_col, y_col, title),
        style={"display": "inline-block"}
    )


layout = html.Div([
    # Überschrift
    html.H1(['Vorhersagen - Analyse']),

    dcc.Interval(id='fig-interval-component', 
                 interval=600_000, # Updates alle 10 Minuten
                 n_intervals=0),  

    html.Div(id='figures-container')
])

# Callback zur Aktualisierung der Vorhersage-Grafik
@callback(
    Output("figures-container", "children"),
    [Input("fig-interval-component", "n_intervals")]
)

def update_layout(n):
    """
    Aktualisiert die Vorhersage-Grafik

    Parameters:
    - n (int): Anzahl der Intervall-Zeiten, die seit dem Start vergangen sind.

    Returns:
    - list: Liste von dcc.Graph-Komponenten, die die aktualisierten Vorhersage-Grafiken darstellen.
    """

    df = get_data_from_postgres()
    
    # Vorhersageparameter
    forecasts = [
        ('createdat', 'temperatur', 'Temperatur °C'),
        ('createdat', 'relluftfeuchte', 'Rel. Luftfeuchte %'),
        ('createdat', 'luftdruck', 'Luftdruck hPa'),
        ('createdat', 'uvintensität', 'UV-Intensität μW/cm²')
    ]
    
    # Multiprocessing Pool für parallele Verarbeitung starten
    pool = multiprocessing.Pool(processes=len(forecasts))
    figures = pool.starmap(process_forecast, [(df,) + params for params in forecasts])
    pool.close()
    pool.join()
    
    return figures
