import dash
from dash import dcc, html, callback, Output, Input
import pandas as pd
from neuralprophet import NeuralProphet
import plotly.express as px
import sqlalchemy
from functions import get_data_from_postgres, neural_prophet_forecast
import pickle
import os

dash.register_page(__name__, name='Modell')



# Laden der Daten
df = get_data_from_postgres()

# Layout der Dash-App definieren
layout = html.Div([
    html.H1(['Vorhersagen - Analyse']),
    dcc.Interval(id='fig-interval-component', interval=600_000, n_intervals=0),  # Intervall auf 10 Minuten gesetzt
    html.Div([
            dcc.Graph(id='fig1', figure=neural_prophet_forecast(df, 'createdat', 'temperatur', 'Temperatur °C'), style={"display": "inline-block"}),
            dcc.Graph(id='fig2', figure=neural_prophet_forecast(df, 'createdat', 'relluftfeuchte', 'Rel. Luftfeuchte %'), style={"display": "inline-block"})
        ], className="row", style={"margin-bottom": "20px"}),
        html.Div([
            dcc.Graph(id='fig3', figure=neural_prophet_forecast(df, 'createdat', 'luftdruck', 'Luftdruck hPa'), style={"display": "inline-block"}),
            dcc.Graph(id='fig4', figure=neural_prophet_forecast(df, 'createdat', 'uvintensität', 'UV-Intensität μW/cm²'), style={"display": "inline-block"})
        ], className="row", style={"margin-bottom": "20px"})
    ])

@callback(
    [
        Output("fig1", "figure"),
        Output("fig2", "figure"),
        Output("fig3", "figure"),
        Output("fig4", "figure")
    ],
    [
        Input("fig-interval-component", "n_intervals"),
    ]
)
def update_layout(n):
    df = get_data_from_postgres()
    
    # Figuren aktualisieren
    fig1 = neural_prophet_forecast(df, 'createdat', 'temperatur', 'Temperatur °C')
    fig2 = neural_prophet_forecast(df, 'createdat', 'relluftfeuchte', 'Rel. Luftfeuchte %')
    fig3 = neural_prophet_forecast(df, 'createdat', 'luftdruck', 'Luftdruck hPa')
    fig4 = neural_prophet_forecast(df, 'createdat', 'uvintensität', 'UV-Intensität μW/cm²')
    
    return fig1, fig2, fig3, fig4
