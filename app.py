import json
import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table

# Read the GeoJSON file
with open(os.path.join("Data", "stockholm_kommundel_response_date.geojson"), encoding="utf-8") as f:
    geojson = json.load(f)

# Convert GeoJSON to DataFrame
properties = [feature["properties"] for feature in geojson["features"]]
df = pd.DataFrame(properties)

fig = px.choropleth_map(
    df,
    geojson=geojson,
    locations="omr_namn",         # column in df
    color=r"% deltagande",              # column in df
    featureidkey="properties.omr_namn",  # key in GeoJSON properties
    map_style="basic",
    zoom=7,
    center={"lat": 59.3293, "lon": 18.0686},  # Example: Stockholm center
    opacity=0.5,
    hover_name="omr_namn",                # Optional
    hover_data={
        "omr_namn": False,        # hide this
        "% deltagande": True,      # hide this
        "sdk_text": True
    },
    color_continuous_scale=px.colors.sequential.Reds,
)

app = dash.Dash(__name__)
app.title = "FHE 2021 response rate"

app.layout = html.Div([
    html.H1("Response rate on folkhälsoenkät 2021", style={'textAlign': 'center'}),

    html.Div(
        style={
            'display': 'flex',
            'flexDirection': 'row',
            'gap': '20px',
            'height': '90vh',          # Almost full viewport height minus header
            'padding': '5px'
        },
        children=[

            html.Div(
                dcc.Graph(
                    figure=fig,
                    # Make Graph fill the div height
                    style={'height': '100%', 'margin': '0', 'padding': '0'}
                ),
                style={
                    'flex': '1',
                    'height': '100%',
                    'minWidth': '0',
                    'margin': '0',       # remove margin here
                    'padding': '0'  # Important to allow flex children to shrink properly
                }
            ),

            html.Div(
                dash_table.DataTable(
                    columns=[{"name": c, "id": c} for c in df.columns],
                    data=df.to_dict("records"),
                    sort_action="native",
                    page_size=20,
                    style_table={
                        'height': '100%',
                        'overflowY': 'auto',
                        'minWidth': '0'
                    },
                    style_cell={'textAlign': 'left',
                                'whiteSpace': 'normal', 'height': 'auto'}
                ),
                style={
                    'flex': '1',
                    'height': '100%',
                    'minWidth': '0'
                }
            ),
        ]
    )
])

if __name__ == "__main__":
    app.run(debug=False)
