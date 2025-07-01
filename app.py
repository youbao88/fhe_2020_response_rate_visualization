import json
import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table
from flask_caching import Cache

app = dash.Dash(__name__)
app.title = "FHE 2021 response rate"

# Set up Flask-Caching
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 10
})

@cache.memoize(timeout=3600)
def load_geojson():
    with open(os.path.join("Data", "stockholm_kommundel_response_date.geojson"), encoding="utf-8") as f:
        geojson = json.load(f)
    return geojson

@cache.memoize(timeout=3600)
def get_dataframe():
    geojson = load_geojson()
    # Only keep necessary columns
    properties = [
        {
            "omr_namn": feat["properties"]["omr_namn"],
            "% deltagande": feat["properties"]["% deltagande"],
            "sdk_text": feat["properties"].get("sdk_text", "")
        }
        for feat in geojson["features"]
    ]
    return pd.DataFrame(properties), geojson

@cache.memoize(timeout=3600)
def get_figure():
    df, geojson = get_dataframe()
    fig = px.choropleth_map(
        df,
        geojson=geojson,
        locations="omr_namn",
        color=r"% deltagande",
        featureidkey="properties.omr_namn",
        map_style="basic",
        zoom=7,
        center={"lat": 59.3293, "lon": 18.0686},
        opacity=0.5,
        hover_name="omr_namn",
        hover_data={
            "omr_namn": False,
            "% deltagande": True,
            "sdk_text": True
        },
        color_continuous_scale=[
            [0.0, "red"],
            [0.5, "white"],
            [1.0, "blue"]
        ],
        color_continuous_midpoint=35,
        range_color=[20, 67]
    )
    return fig, df

fig, df = get_figure()

app.layout = html.Div([
    html.H1("Response rate on folkhälsoenkät 2021",
            style={'textAlign': 'center'}),

    html.Div(
        style={
            'display': 'flex',
            'flexDirection': 'row',
            'gap': '20px',
            'height': '90vh',
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
                    'flex': '1',  # Changed from '1' to '2' for wider map
                    'height': '100%',
                    'minWidth': '0',
                    'margin': '0',
                    'padding': '0'
                }
            ),

            html.Div(
                dash_table.DataTable(
                    columns=[{"name": c, "id": c} for c in df.columns],
                    data=df.to_dict("records"),
                    sort_action="native",
                    filter_action='native',
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
    app.run(debug=True)
