import dash
from dash import dcc, html, callback, Output, Input
from functions import get_data_from_postgres, neural_prophet_forecast
import multiprocessing

dash.register_page(__name__, name='Modell')

# Laden der Daten
df = get_data_from_postgres()

# Funktion zum Verarbeiten einer Vorhersage
def process_forecast(df, x_col, y_col, title):
    return dcc.Graph(
        figure=neural_prophet_forecast(df, x_col, y_col, title),
        style={"display": "inline-block"}
    )

# Layout der Dash-App definieren
layout = html.Div([
    html.H1(['Vorhersagen - Analyse']),
    dcc.Interval(id='fig-interval-component', interval=600_000, n_intervals=0),  # Intervall auf 10 Minuten gesetzt
    html.Div(id='figures-container')
])

@callback(
    Output("figures-container", "children"),
    [Input("fig-interval-component", "n_intervals")]
)
def update_layout(n):
    df = get_data_from_postgres()
    
    # Vorhersageparameter
    forecasts = [
        ('createdat', 'temperatur', 'Temperatur °C'),
        ('createdat', 'relluftfeuchte', 'Rel. Luftfeuchte %'),
        ('createdat', 'luftdruck', 'Luftdruck hPa'),
        ('createdat', 'uvintensität', 'UV-Intensität μW/cm²')
    ]
    
    # Prozesse starten
    pool = multiprocessing.Pool(processes=len(forecasts))
    figures = pool.starmap(process_forecast, [(df,) + params for params in forecasts])
    pool.close()
    pool.join()
    
    return figures
