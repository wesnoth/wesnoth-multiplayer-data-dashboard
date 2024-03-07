import dash
from dash import html

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table


dash.register_page(__name__, path="/query")


column_names = [
    'INSTANCE_UUID', 
    'GAME_ID', 
    'INSTANCE_VERSION', 
    'GAME_NAME', 
    'START_TIME', 
    'END_TIME', 
    'REPLAY_NAME', 
    'OOS', 
    'RELOAD', 
    'OBSERVERS', 
    'PASSWORD', 
    'PUBLIC', 
    'GAME_DURATION',
]


layout = html.Div(
    id='content-container',
    children=[
        html.Div(
            id='date-picker-container',
            children=[
                html.Label(
                    id="date-picker-label",
                    children="Specify a Date Range"
                ),
                dcc.DatePickerRange(id='date-picker')
            ]
        ),
        dbc.Row([
            dcc.Loading(
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": column, "id": column}
                                for column in column_names],
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_deletable=True,
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    export_format="csv",
                ),
            )
        ]),
        dbc.Col(
            dbc.Card(
                dcc.Loading(
                    dbc.CardBody([
                        html.H5("Total Number of Games",
                                className="card-title"),
                        html.P(id="total-games-value",
                                className="card-text"),
                    ])
                ),
                className="shadow-sm mb-4 bg-white rounded mt-4",
                id='total-games-card'
            ),
            lg=2,
        ),
        html.Div([
            dbc.Row([
                dbc.Col(
                    id='histogram-container',
                    children=[
                        dbc.Card(
                            dcc.Loading(
                                dbc.CardBody(
                                    dcc.Graph(
                                        id='game-duration-histogram')
                                )
                            ),
                            className="shadow-sm mb-4 bg-white rounded",
                        )
                    ],
                )
            ]),
        ])
    ]
),
