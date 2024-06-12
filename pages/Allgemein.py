import dash
from dash import dcc, html, callback, Output, Input, dash_table
import plotly.graph_objects as go
from config import sensebox
from functions import get_data_from_postgres, create_last_measurement_data

dash.register_page(__name__, path="/", name="Allgemein")  # '/' is home page

df = get_data_from_postgres()
# Annahmen für fehlende Variablen
measurements = len(df)
# letzter Messpunkt
last_measurement = create_last_measurement_data()

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
        "width": "50%",
        "margin": "auto",
        "textAlign": "center",
        "padding": "15px",
        "position": "absolute",
        "top": "75%",
        "left": "50%",
        "transform": "translate(-50%, -50%)",
    },
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
        html.Div(id='measurement-info', children=[
            html.P([html.B("Measurements: "), html.Span(id="measurements-text")])
        ]),
        html.P([html.B("Aktuelle Messwerte")]),
        html.Div(id='sensor-table-container', children=[
            dash_table.DataTable(last_measurement.to_dict('records'), columns=[{"name": i, "id": i} for i in last_measurement.columns])
        ]),
        html.Div(
            dcc.Graph(
                id="map-graph",
                figure=map_figure,  
                style={"width": "100%", "height": "auto", "margin": "auto"},
            )
        ),
        html.Div(
            [
                html.P("Hier ist der Link zur Station"),
                dcc.Link(
                    "Opensensemap",
                    href="https://opensensemap.org/explore/6645db6eeb5aad0007a6e4b6",
                ),
                html.Br(),
                html.Img(
                    src="https://sensebox.de/images/logos/sensebox_wort_logo.svg",
                    style={"width": "50%", "height": "auto", "margin": "auto"},
                ),
            ]
        ),
        html.P("Ein Projekt von Evelyn, Alex und Rafael"),
        dcc.Interval(
            id='interval-component',
            interval=60*1000, 
            n_intervals=0
        )
    ],
)

@callback(
    [Output("measurements-text", "children"),
     Output("sensor-table-container", "children")],
    [Input("interval-component", "n_intervals")])
    
def update_measurement_info(n):
    last_measurement = create_last_measurement_data()
    
    # Aktualisierte Daten für die Tabelle
    table_data = last_measurement.to_dict('records')
    columns = [{"name": i, "id": i} for i in last_measurement.columns]
    df = get_data_from_postgres()
    measurements = len(df)
    return f"{measurements}", dash_table.DataTable(data=table_data, columns=columns)

