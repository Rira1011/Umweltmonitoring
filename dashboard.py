import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from config import sensebox
import procesing
import fetch


opensense_df = data = procesing.clean_data(fetch.fetch_sensebox_data())

# Function to create a figure
def create_figure(df, x, y, title, y_title, y2_title=None):
    fig = px.line(df, x=x, y=y, title=title)
    fig.update_xaxes(title_text='Messzeitpunkte')
    fig.update_xaxes(tickangle=45, tickformat='%Y-%m-%d')
    fig.update_layout(
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGrey'),
        annotations=[dict(xref='paper', yref='paper', x=0.5, y=0.0, showarrow=False, text="Hinweis: Ausreißer wurden entfernt")]
    )
    if y2_title:
        fig.add_scatter(x=df[x], y=df[y2_title], mode='lines', name=y2_title, yaxis='y2')
        fig.update_layout(yaxis=dict(title=y_title), yaxis2=dict(title=y2_title, overlaying='y', side='right'))
    else:
        fig.update_yaxes(title_text=y_title)
    return fig

# Create the figures
temp_figure = create_figure(opensense_df, 'createdAt', 'Temperatur', 'Temperaturverlauf (°C) über Zeit', 'Temperatur (°C)')
temp_humid_figure = create_figure(opensense_df, 'createdAt', ['Temperatur'], 'Temperatur und rel. Luftfeuchte über Zeit', 'Temperatur (°C)', 'rel. Luftfeuchte')
temp_uv_figure = create_figure(opensense_df, 'createdAt', ['Temperatur'], 'Temperatur und UV-Intensität über Zeit', 'Temperatur (°C)', 'UV-Intensität')
pressure_humid_figure = create_figure(opensense_df, 'createdAt', ['Luftdruck'], 'Luftdruck und rel. Luftfeuchte über Zeit', 'Luftdruck (hPa)', 'rel. Luftfeuchte')

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout definition
app.layout = html.Div([
    # Sidebar on the left side
    html.Div(
        id='side-panel',
        style={
            'width': '25%',  
            'position': 'fixed',  
            'top': 0,  
            'left': 0,  
            'bottom': 0,  
            'backgroundColor': '#f0f0f0', 
            'overflowY': 'scroll'  
        },
        children=[
            html.Div([
                html.H2('Umweltmonitoring SS24 Projektarbeit'),
                html.P('Im Rahmen eines Fachpraktikums wurde eine OpenSenseBox zur Umweltüberwachung aufgebaut, um Daten wie Luftqualität und Temperatur zu erfassen und zu visualisieren. Die Echtzeitvisualisierung bietet Einblicke in lokale Umweltbedingungen. Ein weiteres Ziel ist die Entwicklung eines Modells zur Wettervorhersage basierend auf diesen Daten.'),
                html.Img(
                    src='https://docs.sensebox.de/images/2020-10-16-opensensemap-faq/openSenseMap_github.png',
                    style={
                        'width': '200px',  
                        'height': '90px'
                    }
                ),
                html.P(f"Anzahl der Messpunkte: {opensense_df.attrs["num_measurments"]}"),
                html.P(f"Anzahl der Fehlerhaften Messungen: {opensense_df.attrs["num_outliers"]}"),
                html.P(f"Anteil der Fehlerhaften Messungen: {opensense_df.attrs["percent_outliers"]}%"),
                html.P("Sensoren:"),
                html.Ul([
                    html.Li(f"{sensebox.SENSOR_INFO[sensor_id]['name']} ({sensebox.SENSOR_INFO[sensor_id]['unit']})")
                    for sensor_id in sensebox.SENSOR_INFO.keys()
                ]),
                html.P("Beispiel text"),
            ], style={'padding': '20px'}),
            html.Footer("Gruppe: Alexandru, Evelyn, Rafael", style={'textAlign': 'left', 'paddingLeft': '20px'})  
        ]
    ),
    
    # Main content on the right side
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id='temp-figure', figure=temp_figure), width=6),
                dbc.Col(dcc.Graph(id='temp-humid-figure', figure=temp_humid_figure), width=6)
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='temp-uv-figure', figure=temp_uv_figure), width=6),
                dbc.Col(dcc.Graph(id='pressure-humid-figure', figure=pressure_humid_figure), width=6)
            ])
        ], fluid=True)
    ], style={'marginLeft': '25%', 'padding': '10px'})  
])

# Interval component for auto-updating the graphs
interval = dcc.Interval(id='interval-component', interval=60_000, n_intervals=0)

# Add interval component to the layout
app.layout.children.append(interval)

# Callback function to update the figures
@app.callback(
    [Output('temp-figure', 'figure'),
     Output('temp-humid-figure', 'figure'),
     Output('temp-uv-figure', 'figure'),
     Output('pressure-humid-figure', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_figures(n_intervals, sense_df):
    sense_df['createdAt'] = pd.to_datetime(sense_df['createdAt'])
    sense_df['sensor_name'] = sense_df['Id'].map(lambda x: sensebox.SENSOR_INFO[x]['name'])
    sense_df['unit'] = sense_df['Id'].map(lambda x: sensebox.SENSOR_INFO[x]['unit'])

    sense_df = sense_df[sense_df['outlier'] != True]

    opensense_df = sense_df.pivot_table(
        index='createdAt',
        columns='sensor_name',
        values='value'
    ).reset_index()

    temp_figure = create_figure(opensense_df, 'createdAt', 'Temperatur', 'Temperaturverlauf (°C) über Zeit', 'Temperatur (°C)')
    temp_humid_figure = create_figure(opensense_df, 'createdAt', ['Temperatur'], 'Temperatur und rel. Luftfeuchte über Zeit', 'Temperatur (°C)', 'rel. Luftfeuchte')
    temp_uv_figure = create_figure(opensense_df, 'createdAt', ['Temperatur'], 'Temperatur und UV-Intensität über Zeit', 'Temperatur (°C)', 'UV-Intensität')
    pressure_humid_figure = create_figure(opensense_df, 'createdAt', ['Luftdruck'], 'Luftdruck und rel. Luftfeuchte über Zeit', 'Luftdruck (hPa)', 'rel. Luftfeuchte')

    return temp_figure, temp_humid_figure, temp_uv_figure, pressure_humid_figure

if __name__ == '__main__':
    app.run_server(debug=True)
