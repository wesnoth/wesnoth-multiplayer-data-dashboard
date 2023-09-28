import os
import sys

import dash_bootstrap_components as dbc
import mariadb
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, callback, dash_table, dcc, html


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
        print(f"Error connecting to MariaDB Platform: {error}")
        sys.exit(1)

    return conn.cursor()


def create_app():
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    cursor = create_mariadb_cursor()
    cursor.execute("SHOW COLUMNS FROM tmp_game_info;")
    column_names = [i[0] for i in cursor.fetchall()]
    cursor.connection.close()
    app.layout = create_app_layout(column_names)

    return app


def create_app_layout(column_names):
    layout = dbc.Container([
        html.H1("Wesnoth Multiplayer Statistics"),
        html.Hr(),
        dbc.Row([
            dcc.DatePickerRange(
                id='date-picker',
            )
        ]),
        dbc.Row([
            html.Div(
                dash_table.DataTable(
                    id='table',
                    columns=[
                        {"name": column, "id": column, "deletable": True, "selectable": True} for column in column_names
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
                    page_size=30,
                    style_table={'overflowX': 'auto'}
                ),
            )
        ])
    ])
    return layout


@callback(
    Output('table', 'data'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date'),
)
def fetch_data(start_date, end_date):
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


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, dev_tools_prune_errors=False)
