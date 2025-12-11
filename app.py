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
    # Ensure this path is correct relative to where you run the script
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
    
    # Accessible color scale: Pink -> Orange -> Yellow
    accessible_scale = [
        [0.0, "#e1056d"],  # Low (Pink)
        [0.5, "#eb9100"],  # Mid (Orange)
        [1.0, "#ffd400"]   # High (Yellow)
    ]

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
        color_continuous_scale=accessible_scale,
        range_color=[20, 67] 
        # Note: color_continuous_midpoint was removed to allow a linear sequential transition
    )

    # Update chart typography to match report standards
    fig.update_layout(
        font=dict(
            family="Verdana",
            size=16,  # Increased font size for chart text
            color="black"
        ),
        # Ensure the color bar (legend) text is also readable
        coloraxis_colorbar=dict(
            title_font=dict(family="Verdana", size=16, color="black"),
            tickfont=dict(family="Verdana", size=14, color="black")
        ),
        margin={"r":0,"t":0,"l":0,"b":0} # Optional: tight layout for printing
    )
    
    return fig, df

fig, df = get_figure()

app.layout = html.Div(
    style={
        # Global Font Settings for the Report
        'fontFamily': 'Verdana, sans-serif',
        'color': '#000000', # Full black
        'fontSize': '16px'  # Base font size increased
    },
    children=[
        html.H1("Response rate on folkhälsoenkät 2021",
                style={'textAlign': 'center', 'fontWeight': 'bold', 'color': '#000000'}),

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
                        style={'height': '100%', 'margin': '0', 'padding': '0'}
                    ),
                    style={
                        'flex': '1',
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
                        style_cell={
                            'textAlign': 'left',
                            'whiteSpace': 'normal', 
                            'height': 'auto',
                            'fontFamily': 'Verdana', # Ensure table uses Verdana
                            'color': 'black',
                            'fontSize': '14px'
                        },
                        style_header={
                            'fontWeight': 'bold',
                            'fontFamily': 'Verdana',
                            'color': 'black',
                            'backgroundColor': '#f9f9f9'
                        }
                    ),
                    style={
                        'flex': '1',
                        'height': '100%',
                        'minWidth': '0'
                    }
                ),
            ]
        )
    ]
)

if __name__ == "__main__":
    app.run(debug=True)