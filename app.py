# Author: BrenoAV
# -*- coding: utf-8 -*-
""" Dash Application to show Load Curve on the screen
"""
import pandas as pd
import plotly.express
from dash import Dash, Input, Output, callback, dcc, html

df = pd.read_csv("./outputs/energy_load_curve_brazil.csv", index_col="din_instante")
df.index = pd.to_datetime(df.index, yearfirst=True)
REGIONS = df.columns.values
YEARS = [str(year) for year in list(range(2000, 2024))]
YEARS.insert(0, "all")

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1(
            children="Load Energy Curves Daily (ONS)",
            style={"textAlign": "center"},
        ),
        html.H2(
            children="Data Visualization Demo, by: BrenoAV",
            style={"textAlign": "center"},
        ),
        html.Div(
            [
                html.Div(
                    dcc.Dropdown(
                        REGIONS, "Nordeste", id="dropdown-selection-region", multi=True
                    ),
                    style={"width": "30%", "display": "inline-block"},
                ),
                html.Div(
                    dcc.Dropdown(
                        YEARS, 2023, id="dropdown-selection-year", clearable=False
                    ),
                    style={"width": "5%", "display": "inline-block"},
                ),
            ]
        ),
        html.Div(dcc.Graph(id="graph-content-load-energy-curve")),
    ]
)


@callback(
    Output("graph-content-load-energy-curve", "figure"),
    [
        Input("dropdown-selection-region", "value"),
        Input("dropdown-selection-year", "value"),
    ],
)
def update_graph(regions, year):
    if year == "all":
        df_year = df.copy()
    else:
        df_year = df.loc[df.index.year == int(year)]
    fig = plotly.express.line(
        df_year,
        x=df_year.index,
        y=regions,
        title="Brazil Energy Load Curve (MW) - Regions",
    ).update_layout(
        xaxis_title="Time (day)",
        yaxis_title="Avg Energy Load (MW)",
        legend=dict(title="Regions"),
    )
    return fig


def main() -> None:
    """Main Function, running the Dash"""
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
