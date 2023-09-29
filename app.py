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
    app = Dash(__name__, external_stylesheets=[
        "https://www.wesnoth.org/wesmere/css/wesmere-1.1.10.css",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
    ])
    app.title = "Wesnoth Multiplayer Dashboard"

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
    layout = dbc.Container([
        dbc.Container(
            html.H1("Wesnoth Multiplayer Dashboard"),
            className='mt-4',
            id='title-container'
        ),
        dbc.Container([
            dbc.Row([
                dbc.Container([
                    html.Label("Specify a Date Range",
                               id="date-picker-label"),
                    dcc.DatePickerRange(id='date-picker')
                ], id='date-picker-container')
            ]),
            dbc.Row([
                dcc.Loading(
                    children=dash_table.DataTable(
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
            dbc.Container(
                children=dcc.Loading(
                    children=[
                        dbc.Container(
                            children=[dcc.Graph(id='game-duration-histogram')],
                            id='histogram-container'
                        ),
                        dbc.Container(
                            children=[
                                dcc.Graph(id='instance_version-chart'),
                                dcc.Graph(id='oos-chart'),
                                dcc.Graph(id='reload-chart'),
                                dcc.Graph(id='observers-chart'),
                                dcc.Graph(id='password-chart'),
                                dcc.Graph(id='public-chart'),
                            ],
                            id='donut-charts-container',
                        ),
                    ]
                )
            )
        ], id='content-container'),
        html.Footer(
            html.Div(
                children=[
                    dcc.Markdown(
                        "This Dashboard is a Single Page Application that uses [Plotly Dash](https://plotly.com/dash/) and [pandas](https://pandas.pydata.org/).",
                        id="plotly-dash-credit"
                    ),
                    dcc.Link(
                        html.Div([
                            html.I(className="fa fa-github"),
                            "  View Source Code on GitHub ",
                            html.I(className="fa fa-external-link"),
                        ]),
                        href="#",
                        target="_blank",
                        id="github-link",
                    ),
                ],
                className='text-center',
                id='footer-container'
            )
        )
    ])
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
    Output('oos-chart', 'figure'),
    Output('reload-chart', 'figure'),
    Output('observers-chart', 'figure'),
    Output('password-chart', 'figure'),
    Output('public-chart', 'figure'),
    Output('game-duration-histogram', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_charts(data, columns):
    df = pd.DataFrame(data, columns=[column['name'] for column in columns])
    instance_version_value_counts = (
        df['INSTANCE_VERSION']
        .value_counts()
        .to_frame()
    )
    oos_value_counts = (
        df['OOS']
        .replace({
            0: 'Did not encounter OOS',
            1: 'Encountered OOS'
        })
        .value_counts()
        .to_frame()
    )
    reload_value_counts = (
        df['RELOAD']
        .replace({
            0: 'New game',
            1: 'Reload of a previous game'
        })
        .value_counts()
        .to_frame()
    )
    observers_value_counts = (
        df['OBSERVERS']
        .replace({
            0: 'Observers not allowed',
            1: 'Observers allowed'
        })
        .value_counts()
        .to_frame()
    )
    password_value_counts = (
        df['PASSWORD']
        .replace({
            0: 'Password not required',
            1: 'Password required'
        })
        .value_counts()
        .to_frame()
    )
    public_value_counts = (
        df['PUBLIC']
        .replace({
            0: 'Replay file was not made public',
            1: 'Replay file was made public'
        })
        .value_counts()
        .to_frame()
    )
    figures = (
        px.pie(
            instance_version_value_counts,
            names=instance_version_value_counts.index,
            values=instance_version_value_counts['count'],
            title='Wesnoth Instance Version',
            hole=0.7,
        ),
        px.pie(
            oos_value_counts,
            names=oos_value_counts.index,
            values=oos_value_counts['count'],
            title='Games with Out-of-Sync Errors',
            hole=0.7,
        ),
        px.pie(
            reload_value_counts,
            names=reload_value_counts.index,
            values=reload_value_counts['count'],
            title='Reloaded Games',
            hole=0.7,
        ),
        px.pie(
            observers_value_counts,
            names=observers_value_counts.index,
            values=observers_value_counts['count'],
            title='Games that Allow Observers',
            hole=0.7,
        ),
        px.pie(
            password_value_counts,
            names=password_value_counts.index,
            values=password_value_counts['count'],
            title='Games Requiring a Password to Join',
            hole=0.7,
        ),
        px.pie(
            public_value_counts,
            names=public_value_counts.index,
            values=public_value_counts['count'],
            title='Games with a Public Replay File',
            hole=0.7,
        ),
        px.histogram(
            df,
            x='GAME_DURATION',
            title='Game Duration (minutes)',
            labels={'GAME_DURATION': 'Duration (minutes)'},
            histnorm='percent',
        ).update_traces(
            marker_line_width=1,
            marker_line_color="white"
        )
    )
    for figure in figures:
        figure.update_layout(
            hoverlabel=dict(
                bgcolor="white",
            )
        )
    return figures


if __name__ == '__main__':
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
