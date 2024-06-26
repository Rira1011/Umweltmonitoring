import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
import procesing
from datetime import datetime
from fetch import get_latest_timestamp, fetch_sensebox_data, update_db

# Erstellen der Dash-Anwendung

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.MINTY])

# Sidebar mit Naigationslinks 
sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [
                html.Div(page["name"], className="ms-2"),
            ],
            href=page["path"],
            active="exact",
        )
        for page in dash.page_registry.values()
    ]
    + [
        # Button um Daten zu aktualisieren 
        dbc.NavLink(
            dbc.Button("Datenbank und Sensordaten aktualisieren", id="update-button", color="primary", className="mt-3 ml-2"),
            href="#",
            active="exact",
            style={"position": "absolute", "bottom": "20px", "left": "20px"},
        )
    ],
    vertical=True,
    pills=True,
    className="bg-light",
    style={
        "position": "fixed",
        "top": 0,
        "bottom": 0,
        "left": 0,
        "width": "200px",
        "padding": "20px",
    },
)

# Layout der gesamten Dash-Anwendung
app.layout = dbc.Container(
    [   # Kopfzeile mit Titel
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        "Umweltmonitoring",
                        style={"fontSize": 50, "textAlign": "center"},
                    )
                )
            ]
        ),

        html.Hr(),

        # Hauptinhalt mit Sidebar und Hauptbereich
        dbc.Row(
            [  
                dbc.Col([sidebar], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),
                dbc.Col([dash.page_container], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10),
            ]
        ),
        dcc.Interval(id='interval-component', interval=10_000, n_intervals=0),
        html.Div(id="update-output") 
    ],
    fluid=True,
)

# Callback-Funktion für den Button zum Aktualisieren der Datenbank und Sensordaten
@app.callback(
    Output("update-output", "children"),
    [Input("update-button", "n_clicks")]
)
def update_data(n_clicks):
    """
    Aktualisierung basierend auf den Button in der Dash-Anwendung

    Returns:
    - str or None: Gibt eine Bestätigungsmeldung zurück, wenn die Daten erfolgreich aktualisiert wurden
    """
    if n_clicks is not None and n_clicks > 0:
        from_date = datetime.fromisoformat(str(get_latest_timestamp())).strftime('%Y-%m-%dT%H:%M:%SZ')
        data = fetch_sensebox_data(from_date=from_date)
        update_db(procesing.clean_data(data))
    else:
        return "Alarm"

if __name__ == "__main__":
    app.run(debug=False)
