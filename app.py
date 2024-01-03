import logging
import os
import sys

import dash_bootstrap_components as dbc
import mariadb
import plotly.express as px
from dash import Dash, Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate


def connect_to_mariadb():
    """
    Connects to a MariaDB database using environment variables for authentication.

    Returns:
    mariadb.connection: A connection object representing the database connection.

    Raises:
    mariadb.Error: An error occurred while connecting to the database.
    """
    try:
        connection = mariadb.connect(
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            database=os.environ["DB_DATABASE"],
        )
        return connection
    except mariadb.Error as error:
        logging.error(f"Error connecting to MariaDB Platform: {error}")
        sys.exit(1)


def create_app():
    """
    Creates a Dash web application instance for the Wesnoth Multiplayer Dashboard.

    This function initializes a Dash web application instance with external stylesheets,
    meta tags, and a layout tailored for displaying Wesnoth multiplayer game data.
    It also fetches column names from the 'wesnothd_game_info' table in a MariaDB database
    to dynamically generate the dashboard's layout.

    Returns:
        Dash: A Dash web application instance.
    """
    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
        ],
        title="Wesnoth Multiplayer Dashboard",
        meta_tags=[
            {
                "name": "description",
                "content": "A dashboard for a database of Wesnoth multiplayer games.",
            }
        ],
    )

    app.layout = create_app_layout()
    return app


def create_app_layout():
    """
    Creates the layout for the Wesnoth Multiplayer Dashboard web application.

    This function defines the structure of the dashboard's user interface, including
    the title, user guide modal, date picker, data table, charts, and footer.

    Args:
        column_names (list): A list of column names for the data table.

    Returns:
        The Dash web application layout.
    """
    with open("./assets/markdown/footer_technology_stack.md", "r") as file:
        footer_technology_stack_markdown = file.read()

    with open("./assets/markdown/user_guide.md", "r") as file:
        user_guide_markdown = file.read()

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
        id="top-level-container",
        children=[
            html.Div(
                id="title-container",
                children=[
                    html.H1("Wesnoth Multiplayer Data"),
                    dbc.Button(
                        children=[
                            html.I(className="fa fa-question-circle"),
                            "  User Guide",
                        ],
                        color="primary",
                        id="user-guide-button",
                        n_clicks=0,
                    ),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(dbc.ModalTitle("User Guide")),
                            dbc.ModalBody(dcc.Markdown(user_guide_markdown)),
                            dbc.ModalFooter(
                                dbc.Button(
                                    "Close",
                                    id="close-button",
                                    className="ms-auto",
                                    n_clicks=0,
                                )
                            ),
                        ],
                        id="modal",
                        is_open=False,
                        size="xl",
                    ),
                ],
                className="d-flex align-items-center justify-content-between",
            ),
            html.Div(
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
            html.Footer(
                id="footer-container",
                children=html.Div(
                    children=[
                        dcc.Markdown(
                            id="plotly-dash-credit",
                            children=footer_technology_stack_markdown,
                            link_target="_blank",
                        ),
                        dbc.Button(
                            id="download-link",
                            children=html.Div(
                                [
                                    html.I(className="fa fa-github"),
                                    "  View Source Code on GitHub ",
                                    html.I(className="fa fa-external-link"),
                                ]
                            ),
                            color="primary",
                            href="#",
                            target="_blank",
                        ),
                    ],
                ),
            ),
        ],
    )
    return layout


""" Callback functions start here """


@callback(
    Output("total-games-value", "children"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
    prevent_initial_call=True,
)
def update_total_games_value(start_date, end_date):
    """
    Updates the total-games-value card displayed on the dashboard.

    When the date range is changed, this function fetches the total count of games played in the given date range from the database,
    formats it to have comma separators, and returns it to be displayed on the dashboard.

    Args:
        start_date (str): The start date of the selected date range.
        end_date (str): The end date of the selected date range.

    Returns:
        str: The count of total games formatted to have comma separators.
    """
    # Validate that both start_date and end_date are not None.
    if start_date is None or end_date is None:
        raise PreventUpdate

    # Fetch the total count of games played in the given date range from the database.
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    target_table = "wesnothd_game_info"
    cursor.execute(
        f"SELECT COUNT(*) FROM {target_table} WHERE START_TIME BETWEEN ? AND ?",
        (start_date, end_date),
    )
    logging.debug(f"Fetched the count of total games from {target_table} from database")
    games_count = cursor.fetchone()[0]
    cursor.close()
    mariadb_connection.close()

    return f"{games_count:,}"


@callback(
    Output("instance_version-chart", "figure"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_instance_version_chart(start_date, end_date):
    """
    Update the instance-version-chart whenever the date range changes.

    Args:
        start_date (str): The start date of the selected date range.
        end_date (str): The end date of the selected date range.

    Returns:
        plotly.graph_objects.Figure: The updated instance-version-chart.
    """
    # Validate that both start_date and end_date are not None.
    if start_date is None or end_date is None:
        return px.pie()  # An empty chart

    # Query the database.
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    target_table = "wesnothd_game_info"
    cursor.execute(
        f"SELECT INSTANCE_VERSION, COUNT(*) FROM {target_table} WHERE START_TIME BETWEEN ? AND ? GROUP BY INSTANCE_VERSION",
        (start_date, end_date),
    )
    logging.debug(
        f"Fetched instance version value counts of {target_table} from database"
    )
    value_counts = cursor.fetchall()  # List of tuples
    cursor.close()
    mariadb_connection.close()

    # Convert list of tuples to dictionary
    instance_version_value_counts = dict(value_counts)

    figure = px.pie(
        names=list(instance_version_value_counts.keys()),
        values=list(instance_version_value_counts.values()),
        title="Wesnoth Instance Version",
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    figure.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,}")
    return figure


@callback(
    Output("oos-chart", "figure"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_oos_chart(start_date, end_date):
    """
    Update the oos-chart whenever the date range changes.

    Args:
        start_date (str): The start date of the selected date range.
        end_date (str): The end date of the selected date range.

    Returns:
        plotly.graph_objects.Figure: The updated oos-chart.
    """
    # Validate that both start_date and end_date are not None.
    if start_date is None or end_date is None:
        return px.pie()  # An empty chart

    # Query the database.
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    target_table = "wesnothd_game_info"
    cursor.execute(
        f"SELECT OOS, COUNT(*) FROM {target_table} WHERE START_TIME BETWEEN ? AND ? GROUP BY OOS",
        (start_date, end_date),
    )
    logging.debug(f"Fetched OOS value counts of {target_table} from database")
    value_counts = cursor.fetchall()  # List of tuples
    cursor.close()
    mariadb_connection.close()

    # Convert list of tuples to dictionary
    oos_value_counts = dict(value_counts)

    # Remap byte keys to string values
    key_mapping = {b"\x00": "Did not encounter OOS", b"\x01": "Encountered OOS"}
    oos_value_counts = {
        key_mapping[key]: value for key, value in oos_value_counts.items()
    }

    figure = px.pie(
        names=list(oos_value_counts.keys()),
        values=list(oos_value_counts.values()),
        title="Games with Out-of-Sync Errors",
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    figure.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,}")
    return figure


@callback(
    Output("reload-chart", "figure"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_reload_chart(start_date, end_date):
    """
    Update the reload-chart whenever the date range changes.

    Args:
        start_date (str): The start date of the selected date range.
        end_date (str): The end date of the selected date range.

    Returns:
        plotly.graph_objects.Figure: The updated reload-chart.
    """
    # Validate that both start_date and end_date are not None.
    if start_date is None or end_date is None:
        return px.pie()  # An empty chart

    # Query the database.
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    target_table = "wesnothd_game_info"
    cursor.execute(
        f"SELECT RELOAD, COUNT(*) FROM {target_table} WHERE START_TIME BETWEEN ? AND ? GROUP BY RELOAD",
        (start_date, end_date),
    )
    logging.debug(f"Fetched RELOAD value counts of {target_table} from database")
    value_counts = cursor.fetchall()  # List of tuples
    cursor.close()
    mariadb_connection.close()

    # Convert list of tuples to dictionary
    reload_value_counts = dict(value_counts)

    # Remap byte keys to string values
    key_mapping = {b"\x00": "New Game", b"\x01": "Reloaded Game"}
    reload_value_counts = {
        key_mapping[key]: value for key, value in reload_value_counts.items()
    }

    figure = px.pie(
        names=list(reload_value_counts.keys()),
        values=list(reload_value_counts.values()),
        title="Reloaded Games",
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    figure.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,}")
    return figure


@callback(
    Output("observers-chart", "figure"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_observers_chart(start_date, end_date):
    """
    Update the observers-chart whenever the date range changes.

    Args:
        start_date (str): The start date of the selected date range.
        end_date (str): The end date of the selected date range.

    Returns:
        plotly.graph_objects.Figure: The updated observers-chart.
    """
    # Validate that both start_date and end_date are not None.
    if start_date is None or end_date is None:
        return px.pie()  # An empty chart

    # Query the database.
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    target_table = "wesnothd_game_info"
    cursor.execute(
        f"SELECT OBSERVERS, COUNT(*) FROM {target_table} WHERE START_TIME BETWEEN ? AND ? GROUP BY OBSERVERS",
        (start_date, end_date),
    )
    logging.debug(f"Fetched OBSERVERS value counts of {target_table} from database")
    value_counts = cursor.fetchall()  # List of tuples
    cursor.close()
    mariadb_connection.close()

    # Convert list of tuples to dictionary
    observers_value_counts = dict(value_counts)

    # Remap byte keys to string values
    key_mapping = {b"\x00": "Observers not allowed", b"\x01": "Observers allowed"}
    observers_value_counts = {
        key_mapping[key]: value for key, value in observers_value_counts.items()
    }

    figure = px.pie(
        names=list(observers_value_counts.keys()),
        values=list(observers_value_counts.values()),
        title="Games that Allow Observers",
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    figure.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,}")
    return figure


@callback(
    Output("password-chart", "figure"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_password_chart(start_date, end_date):
    """
    Update the password-chart whenever the date range changes.

    Args:
        start_date (str): The start date of the selected date range.
        end_date (str): The end date of the selected date range.

    Returns:
        plotly.graph_objects.Figure: The updated password-chart.
    """
    # Validate that both start_date and end_date are not None.
    if start_date is None or end_date is None:
        return px.pie()  # An empty chart

    # Query the database.
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    target_table = "wesnothd_game_info"
    cursor.execute(
        f"SELECT PASSWORD, COUNT(*) FROM {target_table} WHERE START_TIME BETWEEN ? AND ? GROUP BY PASSWORD",
        (start_date, end_date),
    )
    logging.debug(f"Fetched PASSWORD value counts of {target_table} from database")
    value_counts = cursor.fetchall()  # List of tuples
    cursor.close()
    mariadb_connection.close()

    # Convert list of tuples to dictionary
    password_value_counts = dict(value_counts)

    # Remap byte keys to string values
    key_mapping = {b"\x00": "Password not required", b"\x01": "Password required"}
    password_value_counts = {
        key_mapping[key]: value for key, value in password_value_counts.items()
    }

    figure = px.pie(
        names=list(password_value_counts.keys()),
        values=list(password_value_counts.values()),
        title="Games Requiring a Password to Join",
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    figure.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,}")
    return figure


@callback(
    Output("public-chart", "figure"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_public_chart(start_date, end_date):
    """
    Update the public-chart whenever the date range changes.

    Args:
        start_date (str): The start date of the selected date range.
        end_date (str): The end date of the selected date range.

    Returns:
        plotly.graph_objects.Figure: The updated public-chart.
    """
    # Validate that both start_date and end_date are not None.
    if start_date is None or end_date is None:
        return px.pie()  # An empty chart

    # Query the database.
    mariadb_connection = connect_to_mariadb()
    cursor = mariadb_connection.cursor()
    target_table = "wesnothd_game_info"
    cursor.execute(
        f"SELECT PUBLIC, COUNT(*) FROM {target_table} WHERE START_TIME BETWEEN ? AND ? GROUP BY PUBLIC",
        (start_date, end_date),
    )
    logging.debug(f"Fetched PUBLIC value counts of {target_table} from database")
    value_counts = cursor.fetchall()  # List of tuples
    cursor.close()
    mariadb_connection.close()

    # Convert list of tuples to dictionary
    public_value_counts = dict(value_counts)

    # Remap byte keys to string values
    key_mapping = {
        b"\x00": "Replay file was not made public",
        b"\x01": "Replay file was made public",
    }
    public_value_counts = {
        key_mapping[key]: value for key, value in public_value_counts.items()
    }

    figure = px.pie(
        names=list(public_value_counts.keys()),
        values=list(public_value_counts.values()),
        title="Games with a Public Replay File",
        hole=0.7,
    )
    figure.update_layout(
        hoverlabel=dict(
            bgcolor="white",
        )
    )
    figure.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,}")
    return figure


@callback(
    Output("modal", "is_open"),
    Input("user-guide-button", "n_clicks"),
    Input("close-button", "n_clicks"),
    State("modal", "is_open"),
)
def toggle_modal(user_guide_button_clicks, close_button_clicks, is_modal_open):
    """
    Toggles the state of the modal based on the user-guide-button clicks and close-button clicks.

    Args:
        user_guide_button_clicks (int): The number of times the user guide button has been clicked.
        close_button_clicks (int): The number of times the close button has been clicked.
        is_modal_open (bool): The current state of the modal; True for 'open' and False for 'closed'.

    Returns:
        bool: The new state of the modal.
    """
    if user_guide_button_clicks or close_button_clicks:
        return not is_modal_open
    return is_modal_open


def main():
    """
    If you are running this file directly, it is implied that you are developing.
    Place anything that you want to be executed or set only when developing the app here.

    Enables debug logs and runs the app in debug mode. Shows full error tracebacks in the console by setting dev_tools_prune_errors to False.
    The app is served at port 8050 of 127.0.0.1 (localhost) by a development server.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    app = create_app()
    app.run(debug=True, dev_tools_prune_errors=False)


if __name__ == "__main__":
    main()
