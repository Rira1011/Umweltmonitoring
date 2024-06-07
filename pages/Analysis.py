import dash
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import psycopg2
from dash import dcc, html, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import sqlalchemy
from config import datenbank
from functions import get_data_from_postgres, create_figure, correlation_heatmap

dash.register_page(__name__, name="Analysis")    

# Laden der Daten
df = get_data_from_postgres()


# Layout der Dash-App definieren
layout = html.Div([
    html.H1(['Analyse']),
    dbc.Container([
        dbc.Label('Was sind die aktuellen Daten'),
        dash_table.DataTable(df.sort_values(by ='createdat', ascending = False).head(4).to_dict('records'), columns=[{"name": i, "id": i} for i in df.columns], id='tbl1')
    ], className="row", style={"margin-bottom": "20px"}),
    html.Div([
        html.H1(['Zeitreihen - Analyse']),
        dcc.Graph(id='graph1', figure=create_figure(df, "createdat", "temperatur", "Temperaturverlauf (°C) über Zeit", "Temperatur °C"), style={"display": "inline-block"}),
        dcc.Graph(id='graph2', figure=create_figure(df, 'createdat', 'temperatur', 'Temperatur und rel. Luftfeuchte über Zeit', "Temperatur °C", 'relluftfeuchte', 'Rel. Luftfeuchte %'), style={"display": "inline-block"})
    ], className="row", style={"margin-bottom": "20px"}),
    html.Div([
        dcc.Graph(id='graph3', figure=create_figure(df, "createdat", "temperatur", "Temperatur und UV-Intensität über Zeit", "Temperatur °C", "uvintensität", "UV-Intensität μW/cm"), style={"display": "inline-block"}),
        dcc.Graph(id='graph4', figure=create_figure(df, "createdat", "luftdruck", "Luftdruck und rel. Luftfeuchte über Zeit", "Luftdruck hPa", "relluftfeuchte", "Rel. Luftfeuchte %"), style={"display": "inline-block"})
    ], className="row", style={"margin-bottom": "20px"}),
    html.Div([
        html.H1(['Korrelations - Analyse']),
        dcc.Graph(id='graph5', figure=correlation_heatmap(df), style={"display": "inline-block"})
    ], className="row", style={"margin-bottom": "20px"}),
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # Update data every minute
])



@callback(
    [
        Output("tbl1", "data"),
        Output("graph1", "figure"),
        Output("graph2", "figure"),
        Output("graph3", "figure"),
        Output("graph4", "figure"),
        Output("graph5", "figure"),
    ],
    [Input("interval-component", "n_intervals")],
)
def update_graphs(n):
    df = get_data_from_postgres()  # Daten aktualisieren

    # Aktualisierte Daten für die Tabelle
    table_data = df.sort_values(by='createdat', ascending=False).head(4).to_dict('records')
    
    temp_figure = create_figure(df, "createdat", "temperatur", "Temperaturverlauf (°C) über Zeit", "Temperatur °C")
    temp_humid_figure = create_figure(df, 'createdat', 'temperatur', 'Temperatur und rel. Luftfeuchte über Zeit', "Temperatur °C", 'relluftfeuchte', 'Rel. Luftfeuchte %')
    temp_uv_figure = create_figure(df, "createdat", "temperatur", "Temperatur und UV-Intensität über Zeit", "Temperatur °C", "uvintensität", "UV-Intensität μW/cm")
    pressure_humid_figure = create_figure(df, "createdat", "luftdruck", "Luftdruck und rel. Luftfeuchte über Zeit", "Luftdruck hPa", "relluftfeuchte", "Rel. Luftfeuchte %")
    corr_heatmap = correlation_heatmap(df)
    
    return table_data, temp_figure, temp_humid_figure, temp_uv_figure, pressure_humid_figure, corr_heatmap
