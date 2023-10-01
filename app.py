import logging
import os
import sys

import dash_bootstrap_components as dbc
import mariadb
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dash_table, dcc, html


def connect_to_mariadb():
    try:
        connection = mariadb.connect(
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST'],
            port=int(os.environ['DB_PORT']),
            database=os.environ['DB_DATABASE']
        )
        return connection
    except mariadb.Error as error:
        logging.error(f"Error connecting to MariaDB Platform: {error}")
        sys.exit(1)


def create_app():
    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
        ],
        title="Wesnoth Multiplayer Dashboard",
        meta_tags=[
            {
                'name': 'description',
                'content': 'A dashboard for a database of Wesnoth multiplayer games.'
            }
        ]
    )

    # Fetch the column names of the tmp_game_info table.
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    target_table = "tmp_game_info"
    cursor.execute(f"SHOW COLUMNS FROM {target_table};")
    logging.debug(f"Fetched column names of {target_table} from database")
    column_names = [i[0] for i in cursor.fetchall()]
    cursor.close()
    mariadb_connection.close()

    # Add a column for the game duration. It is added this way because the column is not stored in the database and is derived from the START_TIME and END_TIME columns.
    column_names.append("GAME_DURATION")

    app.layout = create_app_layout(column_names)
    return app


def create_app_layout(column_names):
    with open('./assets/markdown/footer_technology_stack.md', 'r') as file:
        footer_technology_stack_markdown = file.read()

    def create_donut_chart_column(figure_id):
        donut_column = dbc.Col(
            dbc.Card(
                dcc.Loading(
                    dbc.CardBody(
                        dcc.Graph(
                            id=figure_id
                        )
                    )
                ),
                className="shadow-sm mb-4 bg-white rounded",
            ),
            sm=12,
            lg=4
        )
        return donut_column

    layout = html.Div(
        id='top-level-container',
        children=[
            html.Div(
                id='title-container',
                children=html.H1("Wesnoth Multiplayer Dashboard")
            ),
            html.Div(
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
                                row_selectable="multi",
                                row_deletable=True,
                                selected_columns=[],
                                selected_rows=[],
                                page_action="native",
                                page_current=0,
                                page_size=10,
                                style_table={'overflowX': 'auto'}
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
                        lg=3,
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
                        html.Div(
                            id='donut-charts-container',
                            children=[
                                dbc.Row([
                                    create_donut_chart_column('instance_version-chart'),
                                    create_donut_chart_column('oos-chart'),
                                    create_donut_chart_column('reload-chart'),
                                ]),
                                dbc.Row([
                                    create_donut_chart_column('observers-chart'),
                                    create_donut_chart_column('password-chart'),
                                    create_donut_chart_column('public-chart'),
                                ]),
                            ],
                        ),
                    ])
                ]
            ),
            html.Footer(
                id='footer-container',
                children=html.Div(
                    children=[
                        dcc.Markdown(
                            id="plotly-dash-credit",
                            children=footer_technology_stack_markdown,
                            link_target="_blank",
                        ),
                        dbc.Button(
                            id="download-link",
                            children=html.Div([
                                html.I(className="fa fa-github"),
                                "  View Source Code on GitHub ",
                                html.I(className="fa fa-external-link"),
                            ]),
                            color="primary",
                            href="#",
                            target="_blank",
                        )
                    ],
                )
            )
        ]
    )
    return layout


@callback(
    Output('table', 'data'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_table(start_date, end_date):
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    cursor.execute(
        "SELECT * FROM tmp_game_info WHERE START_TIME BETWEEN ? AND ?", (start_date, end_date))
    columns = [i[0] for i in cursor.description]
    df = (
        pd.DataFrame(cursor.fetchall(), columns=columns)
        .map(lambda x: x[0] if type(x) is bytes else x)
        .assign(
            START_TIME=lambda x: pd.to_datetime(x['START_TIME']),
            END_TIME=lambda x: pd.to_datetime(x['END_TIME']),
            # Calculate the game duration in minutes.
            GAME_DURATION=lambda x: (
                x['END_TIME'] - x['START_TIME']).dt.total_seconds() / 60,
        )
    )
    logging.debug(df.info())
    cursor.close()
    mariadb_connection.close()
    return df.to_dict('records')


@callback(
    Output('instance_version-chart', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_instance_version_chart(data, columns):
    df = pd.DataFrame(data, columns=[column['name'] for column in columns])
    instance_version_value_counts = (
        df['INSTANCE_VERSION']
        .value_counts()
        .to_frame()
    )
    figure = px.pie(
        instance_version_value_counts,
        names=instance_version_value_counts.index,
        values=instance_version_value_counts['count'],
        title='Wesnoth Instance Version',
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return figure


@callback(
    Output('oos-chart', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_oos_chart(data, columns):
    df = pd.DataFrame(data, columns=[column['name'] for column in columns])
    oos_value_counts = (
        df['OOS']
        .replace({
            0: 'Did not encounter OOS',
            1: 'Encountered OOS'
        })
        .value_counts()
        .to_frame()
    )
    figure = px.pie(
        oos_value_counts,
        names=oos_value_counts.index,
        values=oos_value_counts['count'],
        title='Games with Out-of-Sync Errors',
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return figure


@callback(
    Output('reload-chart', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_reload_chart(data, columns):
    df = pd.DataFrame(data, columns=[column['name'] for column in columns])
    reload_value_counts = (
        df['RELOAD']
        .replace({
            0: 'New game',
            1: 'Reload of a previous game'
        })
        .value_counts()
        .to_frame()
    )
    figure = px.pie(
        reload_value_counts,
        names=reload_value_counts.index,
        values=reload_value_counts['count'],
        title='Reloaded Games',
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return figure


@callback(
    Output('observers-chart', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_observers_chart(data, columns):
    df = pd.DataFrame(data, columns=[column['name'] for column in columns])
    observers_value_counts = (
        df['OBSERVERS']
        .replace({
            0: 'Observers not allowed',
            1: 'Observers allowed'
        })
        .value_counts()
        .to_frame()
    )
    figure = px.pie(
        observers_value_counts,
        names=observers_value_counts.index,
        values=observers_value_counts['count'],
        title='Games that Allow Observers',
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return figure


@callback(
    Output('password-chart', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_password_chart(data, columns):
    df = pd.DataFrame(data, columns=[column['name'] for column in columns])
    password_value_counts = (
        df['PASSWORD']
        .replace({
            0: 'Password not required',
            1: 'Password required'
        })
        .value_counts()
        .to_frame()
    )
    figure = px.pie(
        password_value_counts,
        names=password_value_counts.index,
        values=password_value_counts['count'],
        title='Games Requiring a Password to Join',
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return figure


@callback(
    Output('public-chart', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_public_chart(data, columns):
    df = pd.DataFrame(data, columns=[column['name'] for column in columns])
    public_value_counts = (
        df['PUBLIC']
        .replace({
            0: 'Replay file was not made public',
            1: 'Replay file was made public'
        })
        .value_counts()
        .to_frame()
    )
    figure = px.pie(
        public_value_counts,
        names=public_value_counts.index,
        values=public_value_counts['count'],
        title='Games with a Public Replay File',
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return figure


@callback(
    Output('game-duration-histogram', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_game_duration_histogram(data, columns):
    df = pd.DataFrame(data, columns=[column['name'] for column in columns])
    figure = px.histogram(
        df,
        x='GAME_DURATION',
        title='Game Duration (minutes)',
        labels={'GAME_DURATION': 'Duration (minutes)'},
        histnorm='percent',
    ).update_traces(
        marker_line_width=1,
        marker_line_color="white"
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    return figure


@callback(
    Output('total-games-value', 'children'),
    Input('table', 'data'),
    prevent_initial_call=True
)
def update_total_games_value(data):
    df = pd.DataFrame(data)
    return f"{df.shape[0]:,}"


def main():
    """
    If you are running this file directly, it is implied that you are developing.
    Place anything that you want to be executed or set only when developing the app here.
    """

    # Enable debug logs.
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Run the app in debug mode and show full error tracebacks in the console by setting dev_tools_prune_errors to False.
    app = create_app()
    app.run(debug=True, dev_tools_prune_errors=False)


if __name__ == '__main__':
    main()
