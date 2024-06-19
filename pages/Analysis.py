import dash
from dash import dcc, html, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
from functions import get_data_from_postgres, create_figure, correlation_heatmap
import fetch
import procesing
# Zweite Seite des Dashboards: Analyse der Daten (Visualisierungen)

dash.register_page(__name__, name="Analysis")    

df = procesing.clean_data(fetch.fetch_sensebox_data())


layout = html.Div([

    # Tabelle mit aktuellen Daten
    html.H1(['Analyse']),
    dbc.Container([
        dbc.Label('Was sind die aktuellen Daten'),
        dash_table.DataTable(df.sort_values(by ='createdAt', ascending = False).head(4).to_dict('records'), columns=[{"name": i, "id": i} for i in df.columns], id='tbl1')
    ], className="row", style={"margin-bottom": "20px"}
    ),

    # Visualisierungen (Zeitreihen)
    html.Div([
        html.H1(['Zeitreihen - Analyse']),
        dcc.Graph(id='graph1', 
                  figure=create_figure(df, "createdAt", "Temperatur", "Temperaturverlauf (°C) über Zeit", "Temperatur °C"), 
                  style={"display": "inline-block"}),   

        dcc.Graph(id='graph2', 
                  figure=create_figure(df, 'createdAt', 'Temperatur', 'Temperatur und rel. Luftfeuchte über Zeit', "Temperatur °C", 'rel. Luftfeuchte', 'Rel. Luftfeuchte %'), 
                  style={"display": "inline-block"})

    ], className="row", style={"margin-bottom": "20px"}
    ),
    html.Div([
        dcc.Graph(id='graph3', 
                  figure=create_figure(df, "createdAt", "Temperatur", "Temperatur und UV-Intensität über Zeit", "Temperatur °C", "UV-Intensität", "UV-Intensität μW/cm"), 
                  style={"display": "inline-block"}),
        
        dcc.Graph(id='graph4', 
                  figure=create_figure(df, "createdAt", "Luftdruck", "Luftdruck und rel. Luftfeuchte über Zeit", "Luftdruck hPa", "rel. Luftfeuchte", "Rel. Luftfeuchte %"), 
                  style={"display": "inline-block"})

    ], className="row", style={"margin-bottom": "20px"}
    ),

    # Korrelation von Temperatur und UV-Intensität
    html.Div([
        html.H1(['Korrelations - Analyse']),
        dcc.Graph(id='graph5', 
                  figure=correlation_heatmap(df), 
                  style={"display": "inline-block"})
    ], className="row", style={"margin-bottom": "20px"}
    ),

    # Intervall für regelmäßige Updates
    dcc.Interval(
        id='interval-component', 
        interval=60*1000, # Updates alle 60 Sekunden
        n_intervals=0)  
])


# Callback zur Aktualisierung der Daten und Graphen
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
    """
    Aktualisiert die Grafiken und die Tabelle

    Parameters:
    - n (int): Anzahl der Intervall-Auslösungen für den Callback

    Returns:
    - Daten für die Tabelle, sowie aktualisierte Graphen 
    """

    df = get_data_from_postgres() 

    # aktuelle Daten für Tabelle
    table_data = df.sort_values(by='createdAt', ascending=False).head(4).to_dict('records')
    
    # Graphen aktualisieren
    temp_figure = create_figure(df, "createdAt", "Temperatur", "Temperaturverlauf (°C) über Zeit", "Temperatur °C")
    temp_humid_figure = create_figure(df, 'createdAt', 'Temperatur', 'Temperatur und rel. Luftfeuchte über Zeit', "Temperatur °C", 'rel. Luftfeuchte', 'Rel. Luftfeuchte %')
    temp_uv_figure = create_figure(df, "createdAt", "Temperatur", "Temperatur und UV-Intensität über Zeit", "Temperatur °C", "UV-Intensität", "UV-Intensität μW/cm")
    pressure_humid_figure = create_figure(df, "createdAt", "Luftdruck", "Luftdruck und rel. Luftfeuchte über Zeit", "Luftdruck hPa", "rel. Luftfeuchte", "Rel. Luftfeuchte %")
    corr_heatmap = correlation_heatmap(df)
    
    return table_data, temp_figure, temp_humid_figure, temp_uv_figure, pressure_humid_figure, corr_heatmap
