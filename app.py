# Author: BrenoAV
# -*- coding: utf-8 -*-
""" Dash Application to show Load Curve on the screen
"""
import pandas as pd
import plotly.express
from dash import Dash, Input, Output, callback, dcc, html

df = pd.read_csv("./outputs/energy_load_curve_2022.csv", index_col="din_instante")
REGIONS = df.columns.values

app = Dash(__name__)

# TODO: Adapt this app for the others years

app.layout = html.Div(
    [
        html.H1(children="Load Energy Curves", style={"textAlign": "center"}),
        html.H2(children="Data Visualization Demo", style={"textAlign": "center"}),
        dcc.Dropdown(REGIONS, "Nordeste", id="dropdown-selection-region"),
        dcc.Graph(id="graph-content-load-energy-curve"),
    ]
)


@callback(
    Output("graph-content-load-energy-curve", "figure"),
    Input("dropdown-selection-region", "value"),
)
def update_graph(value):
    # TODO: Appears "Select a valid data" when nothing is selected
    return plotly.express.line(
        df,
        x=df.index,
        y=value,
        title=f"Brazil - Energy load Curve - {value}",
        labels={value: "Avg Energy Load (MW)", "din_instante": "Time (days)"},
    )


def main() -> None:
    """Main Function, running the Dash"""
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
