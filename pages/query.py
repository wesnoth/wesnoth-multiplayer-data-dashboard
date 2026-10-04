import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, register_page
from dash.dash_table.Format import Format, Scheme


register_page(__name__, path="/query", title="Query")


column_config = {
    'INSTANCE_VERSION': {'name': 'Version'},
    'GAME_NAME': {'name': 'Game Name'},
    'GAME_ID': {'name': 'Game ID'},
    'START_TIME': {'name': 'Start Time', 'type': 'text'},
    'END_TIME': {'name': 'End Time', 'type': 'text', 'sort_as_null': ['⚔️ Ongoing']},
    'OOS': {'name': 'OOS'},
    'RELOAD': {'name': 'Reload'},
    'OBSERVERS': {'name': 'Obs'},
    'PASSWORD': {'name': 'Pass'},
    'PUBLIC': {'name': 'Public'},
    'GAME_DURATION': {'name': 'Duration', 'type': 'numeric', 'format': Format(precision=2, scheme=Scheme.fixed)},
    'REPLAY_NAME': {'name': 'Replay Name'},
    'INSTANCE_UUID': {'name': 'Instance UUID'}
}

tooltip_header_config = {
    'OOS': 'Game went out of sync',
    'RELOAD': 'Reloaded Game',
    'OBSERVERS': 'Observers allowed',
    'PASSWORD': 'Password protected',
    'GAME_DURATION': 'Game duration in minutes'
}

layout = html.Div(
    id='content-container',
    children=[
        dbc.Row(
            id="content-first-row",
            children=[
                dbc.Col(
                    id="date-picker-container",
                    children=[
                        html.Label(
                            id="date-picker-label",
                            children="Specify a Date Range"
                        ),
                        dcc.DatePickerRange(id='date-picker-query', updatemode='bothdates')
                    ]
                ),
                dbc.Col(
                    dbc.Card(
                        dcc.Loading(
                            dbc.CardBody([
                                html.H5("Total Number of Games",
                                        className="card-title"),
                                html.P(id="total-games-value-query",
                                        className="card-text"),
                            ])
                        ),
                        className="shadow-sm bg-white rounded",
                        id='total-games-card'
                    ),
                    lg=2,
                ),
            ]
        ),
        dbc.Row([
            dcc.Loading(
                dash_table.DataTable(
                    id='table',
                    columns=[{"id": column, **column_config[column]}
                                for column in column_config],
                    tooltip_header=tooltip_header_config,
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
        ]),
        dcc.Store(id='total-games-integer-value'),
    ]
),
