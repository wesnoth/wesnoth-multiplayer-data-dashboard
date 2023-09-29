import logging
import os
import sys

import dash_bootstrap_components as dbc
import mariadb
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, callback, dash_table, dcc, html


def create_mariadb_cursor():
    try:
        conn = mariadb.connect(
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST'],
            port=int(os.environ['DB_PORT']),
            database=os.environ['DB_DATABASE']
        )
    except mariadb.Error as error:
        logging.error(f"Error connecting to MariaDB Platform: {error}")
        sys.exit(1)

    return conn.cursor()


def create_app():
    app = Dash(__name__, external_stylesheets=[
        "https://www.wesnoth.org/wesmere/css/wesmere-1.1.10.css",
    ])
    app.title = "Wesnoth Multiplayer Dashboard"

    cursor = create_mariadb_cursor()
    target_table = "tmp_game_info"
    cursor.execute(f"SHOW COLUMNS FROM {target_table};")
    logging.debug(f"Fetched column names of {target_table} from database.")
    column_names = [i[0] for i in cursor.fetchall()]
    cursor.connection.close()
    app.layout = create_app_layout(column_names)

    return app


def create_app_layout(column_names):
    logging.debug("Executing create_app_layout()...")
    layout = dbc.Container([
        dbc.Container(
            html.H1("Wesnoth Multiplayer Dashboard"),
            className='mt-4',
            id='title-container'
        ),
        dbc.Container([
            dbc.Row([
                html.Div([
                    html.Label("Specify a Date Range (START_TIME)",
                               id="date-picker-label"),
                    dcc.DatePickerRange(id='date-picker')
                ], id='date-picker-container')
            ]),
            dbc.Row([
                dcc.Loading(
                    children=dash_table.DataTable(
                        id='table',
                        columns=[
                            {"name": column, "id": column, "deletable": False, "selectable": True} for column in column_names
                        ],
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
            html.Div(
                id='charts-container',
                children=[
                    dcc.Loading(
                        children=dcc.Graph(
                            id='oos-chart',
                        )
                    ),
                    dcc.Loading(
                        children=dcc.Graph(
                            id='reload-chart',
                        )
                    ),
                    dcc.Loading(
                        children=dcc.Graph(
                            id='observers-chart',
                        )
                    )
                ]
            )
        ], id='content-container')
    ])
    return layout


@callback(
    Output('table', 'data'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def update_table(start_date, end_date):
    cursor = create_mariadb_cursor()
    cursor.execute(
        "SELECT * FROM tmp_game_info WHERE START_TIME BETWEEN ? AND ?", (start_date, end_date))
    columns = [i[0] for i in cursor.description]
    df = (
        pd.DataFrame(cursor.fetchall(), columns=columns)
        .map(lambda x: x[0] if type(x) is bytes else x)
    )
    cursor.connection.close()
    return df.to_dict('records')


@callback(
    Output('oos-chart', 'figure'),
    Output('reload-chart', 'figure'),
    Output('observers-chart', 'figure'),
    Input('table', 'data'),
    Input('table', 'columns'),
    prevent_initial_call=True
)
def update_charts(data, columns):
    df = pd.DataFrame(data, columns=[c['name'] for c in columns])
    oos_value_counts = (
        df['OOS'].value_counts()
        .to_frame()
    )
    reload_value_counts = (
        df['RELOAD'].value_counts()
        .to_frame()
    )
    observers_value_counts = (
        df['OBSERVERS'].value_counts()
        .to_frame()
    )
    figures = (
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
            title='Observers Allowed',
            hole=0.7,
        ),
    )
    for figure in figures:
        figure.update_layout(
            hoverlabel=dict(
                bgcolor="white",
            )
        )
    return tuple(figures)


if __name__ == '__main__':

    # If you are running this file directly, it is implied that you are developing, thus debug logs are enabled here.
    # You can add other things that you want to be executed or set only when developing the app here.
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    app = create_app()
    app.run(debug=True, dev_tools_prune_errors=False)
