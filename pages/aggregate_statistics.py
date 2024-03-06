import dash
from dash import html

import dash_bootstrap_components as dbc
from dash import dcc, html

dash.register_page(__name__, path="/statistics")


def create_donut_chart_column(figure_id):
    donut_column = dbc.Col(
        dbc.Card(
            dcc.Loading(dbc.CardBody(dcc.Graph(id=figure_id))),
            className="shadow-sm mb-4 bg-white rounded",
        ),
        sm=12,
        lg=4,
    )
    return donut_column


layout = html.Div(
    id="content-container",
    children=[
        html.Div(
            id="date-picker-container",
            children=[
                html.Label(
                    id="date-picker-label", children="Specify a Date Range"
                ),
                dcc.DatePickerRange(id="date-picker"),
            ],
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        dcc.Loading(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Total Number of Games",
                                        className="card-title",
                                    ),
                                    html.P(
                                        id="total-games-value",
                                        className="card-text",
                                    ),
                                ]
                            )
                        ),
                        className="shadow-sm mb-4 bg-white rounded mt-4",
                        id="total-games-card",
                    ),
                    lg=2,
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    id="donut-charts-container",
                    children=[
                        dbc.Row(
                            [
                                create_donut_chart_column(
                                    "instance_version-chart"
                                ),
                                create_donut_chart_column("oos-chart"),
                                create_donut_chart_column("reload-chart"),
                            ]
                        ),
                        dbc.Row(
                            [
                                create_donut_chart_column(
                                    "observers-chart"
                                ),
                                create_donut_chart_column("password-chart"),
                                create_donut_chart_column("public-chart"),
                            ]
                        ),
                    ],
                ),
            ]
        ),
    ],
),
