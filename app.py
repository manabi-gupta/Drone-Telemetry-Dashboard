import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import pandas as pd

# -----------------------------
# LOAD TELEMETRY DATA
# -----------------------------
DF = pd.read_excel("telemetry_data.xlsx")

# Convert TimeStamp → datetime
DF["datetime"] = pd.to_datetime(DF["TimeStamp"], format="%Y-%m-%d_%H-%M-%S.%f")

# -----------------------------
# DASH APP SETUP
# -----------------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([

    html.H2("Drone Telemetry Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Button("Start", id="start", n_clicks=0),
        html.Button("Pause", id="pause", n_clicks=0),
        html.Button("Reset", id="reset", n_clicks=0),
        html.Span(id="status", style={"marginLeft": "20px"})
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    dcc.Interval(id="timer", interval=500, disabled=True),
    dcc.Store(id="idx", data=0),

    html.Div([
        dcc.Graph(id="orientation", style={"width": "65%", "display": "inline-block"}),
        dcc.Graph(id="altitude", style={"width": "33%", "display": "inline-block"})
    ]),

    dcc.Graph(id="map"),
    html.Div(id="readout")
])

# -----------------------------
# CONTROL BUTTONS
# -----------------------------
@app.callback(
    Output("timer", "disabled"),
    Output("status", "children"),
    Input("start", "n_clicks"),
    Input("pause", "n_clicks"),
    Input("reset", "n_clicks"),
)
def control(start, pause, reset):
    ctx = dash.callback_context
    if not ctx.triggered:
        return True, "Stopped"
    btn = ctx.triggered[0]["prop_id"].split(".")[0]

    if btn == "start":
        return False, "Running"
    if btn == "pause":
        return True, "Paused"
    if btn == "reset":
        return True, "Reset"

    return True, "Stopped"

# -----------------------------
# UPDATE INDEX
# -----------------------------
@app.callback(
    Output("idx", "data"),
    Input("timer", "n_intervals"),
    State("idx", "data"),
    State("timer", "disabled")
)
def update_index(n, idx, disabled):
    if disabled:
        return idx
    if idx + 1 >= len(DF):
        return 0
    return idx + 1

# -----------------------------
# MAIN DASHBOARD UPDATE
# -----------------------------
@app.callback(
    Output("orientation", "figure"),
    Output("altitude", "figure"),
    Output("map", "figure"),
    Output("readout", "children"),
    Input("idx", "data")
)
def update_dashboard(i):

    row = DF.iloc[i]
    df_slice = DF.iloc[:i+1]

    # --- ORIENTATION GRAPH ---
    ori = go.Figure()
    ori.add_trace(go.Scatter(x=df_slice["datetime"], y=df_slice["PlatformRoll"], name="Roll"))
    ori.add_trace(go.Scatter(x=df_slice["datetime"], y=df_slice["PlatformPitch"], name="Pitch"))
    ori.add_trace(go.Scatter(x=df_slice["datetime"], y=df_slice["PlatformHeading"], name="Heading"))
    ori.update_layout(title="Orientation")

    # --- ALTITUDE GRAPH ---
    alt = go.Figure()
    alt.add_trace(go.Scatter(
        x=df_slice["datetime"],
        y=df_slice["SensorTrueAltitude"],
        name="Altitude"
    ))
    alt.update_layout(title="Altitude (m)")

    # --- MAP GRAPH ---
    mp = go.Figure()
    mp.add_trace(go.Scattermapbox(
        lat=df_slice["SensorLatitude"],
        lon=df_slice["SensorLongitude"],
        mode="markers+lines",
        marker=dict(size=8)
    ))

    mp.add_trace(go.Scattermapbox(
        lat=[row["SensorLatitude"]],
        lon=[row["SensorLongitude"]],
        mode="markers",
        marker=dict(size=12, color="red")
    ))

    mp.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": row["SensorLatitude"], "lon": row["SensorLongitude"]},
        mapbox_zoom=13,
        title="GPS Path"
    )

    # --- DATA READOUT TABLE ---
    readout = html.Table([
        html.Tr([html.Th("Field"), html.Th("Value")])
    ] + [
        html.Tr([html.Td(k), html.Td(str(v))]) for k, v in row.to_dict().items()
    ])

    return ori, alt, mp, readout


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
