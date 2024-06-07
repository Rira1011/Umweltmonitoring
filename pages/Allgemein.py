import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import psycopg2
import pandas as pd
import sqlalchemy
from config import sensebox
import fetch
from functions import get_data_from_postgres, neural_prophet_forecast

dash.register_page(__name__, path="/", name="Allgemein")  # '/' is home page

df = get_data_from_postgres()
# Annahmen für fehlende Variablen
measurements = len(df)



# Erstellen der Karte
map_figure = go.Figure(
    go.Scattermapbox(
        lat=[sensebox.STATION_LOCATION["latitude"]],
        lon=[sensebox.STATION_LOCATION["longitude"]],
        mode="markers",
        marker=go.scattermapbox.Marker(size=14),
        text=["Station Standort"],
    )
)
map_figure.update_layout(
    hovermode="closest",
    mapbox=dict(
        style="open-street-map",
        center=dict(
            lat=sensebox.STATION_LOCATION["latitude"], lon=sensebox.STATION_LOCATION["longitude"]
        ),
        zoom=15,
    ),
)





# Combined layout
layout = html.Div(
    id="main-content",
    style={
        "width": "50%",  # Breite des Hauptinhalts
        "margin": "auto",  # Zentrieren des Inhalts horizontal
        "textAlign": "center",  # Zentrieren des Textes
        "padding": "15px",  # Abstand um den Inhalt herum
        "position": "absolute",  # Position absolut
        "top": "75%",  # 
        "left": "50%",  # Von links 50% entfernt
        "transform": "translate(-50%, -50%)",  # Zentrieren des Inhalts
    },
    # Einleitungstext
    children=[
        html.H2("Sommersemester 24 Projektarbeit"),
        html.P(
            """Im Rahmen eines Fachpraktikums wurde ein Dashboard,
               mit Informationen einer angelegten Opensensebox Sensorbox erstellt."""
        ),
        html.P(
            """Daten, die außerhalb eines bestimmten Bereichs liegen,
               werden als Ausreißer gekennzeichnet, um Probleme im Datensatz
               für das Machine-Learning-Modell zu vermeiden."""
        ),
        # Infos über die Messung
        html.Div(id='measurement-info', children=[
            html.P([html.B("Measurements: "), html.Span(id="measurements-text")])
        ]),
        html.P([html.B("Sensoren: ")]),
       html.Ul([
            html.P(f"• {sensebox.SENSOR_INFO[sensor_id]['name']} ({sensebox.SENSOR_INFO[sensor_id]['unit']})")
            for sensor_id in sensebox.SENSOR_INFO.keys()
        ]),
        # Map
        html.Div(
            dcc.Graph(
                id="map-graph",
                figure=map_figure,
                style={"width": "100%", "height": "auto", "margin": "auto"},
            )
        ),
        # Bild und Link zur Station
        html.Div(
            [
                html.P("Hier ist der Link zur Station"),
                dcc.Link(
                    "Opensensemap",
                    href="https://opensensemap.org/explore/6645db6eeb5aad0007a6e4b6",
                ),
                html.Br(),  
                html.Img(
                    src="https://cdn.book-family.de/petbook/data/uploads/2022/07/gettyimages-667300283.jpg?impolicy=channel&imwidth=992",
                    style={"width": "50%", "height": "auto", "margin": "auto"},
                ),
            ]
        ),
        html.P("Ein Projekt von Evelyn, Alex und Rafael"),
        dcc.Interval(
            id='interval-component',
            interval=10*1000, 
            n_intervals=0
        )
    ],
)

@callback(
    [Output("measurements-text", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_measurement_info(n):
    df = get_data_from_postgres()
    measurements = len(df)
    return [f"{measurements}"]
