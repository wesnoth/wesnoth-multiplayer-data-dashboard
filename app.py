"""
This script creates and runs the Dash application for the Wesnoth MP Database Dashboard.

Usage:

For development:
    Run `python app.py` to start the development server.

For production:
    Run `gunicorn --bind :$PORT app:server` to start the production server, where $PORT specifies the port number.

Note: Gunicorn only runs on Linux/Unix systems. For Windows, use `waitress` instead, or use a Linux container/VM to run Gunicorn.
"""

import json
import logging
import os
import sys

import mariadb
import plotly.express as px
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
from flask_caching import Cache

from layout import create_app


app = create_app()
server = app.server

# Set up Flask-Caching for sharing data between callbacks
# Refer to the documentation for more information:
# Dash documentation: https://dash.plotly.com/sharing-data-between-callbacks
# Flask-Caching documentation: https://flask-caching.readthedocs.io/en/latest/
CACHE_CONFIG = {
    "CACHE_TYPE": "SimpleCache",  # SimpleCache stores cached data in memory as a Dictionary.
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


@cache.memoize()
def get_target_table():
    """Fetches and returns the database table name from the configuration options file."""
    logging.debug(
        "get_target_table called"
    )  # This only gets logged the first time the function is called and proves that memoization is functioning.
    with open(".config/config.json", "r") as f:
        config = json.load(f)
    target_table = config["table_names_map"]["game_info"]
    return target_table


def connect_to_mariadb():
    """
    Connects to a MariaDB database using defaults, a .json file, or environment variables, for authentication.

    The function first sets default configuration.
    Then it tries to load configuration from a .json file.
    Then it tries to load configuration from environment variables.
    Finally, it tries to load configuration from command line parameters.

    Returns:
    mariadb.connection: A connection object representing the database connection.

    Raises:
    mariadb.Error: An error occurred while connecting to the database.
    """
    try:
        # Set default configuration
        config = {
            "user": None,
            "password": None,
            "host": "127.0.0.1",
            "port": 3306,
            "database": None,
        }

        # Try to load configuration from .json file
        if os.path.isfile(".config/db_config.json"):
            with open(".config/db_config.json", "r") as f:
                file_config = json.load(f)
                # Only update config with values that are not None
                config.update(
                    {
                        key: value
                        for key, value in file_config.items()
                        if value is not None
                    }
                )

        # Try to load configuration from environment variables
        env_config = {
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD"),
            "host": os.environ.get("DB_HOST"),
            "port": int(os.environ.get("DB_PORT"))
            if os.environ.get("DB_PORT")
            else None,
            "database": os.environ.get("DB_DATABASE"),
        }
        # Only update config with values that are not None
        config.update(
            {key: value for key, value in env_config.items() if value is not None}
        )

        connection = mariadb.connect(**config)
        return connection
    except mariadb.Error as error:
        logging.error(f"Error connecting to MariaDB Platform: {error}")
        sys.exit(1)


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
    target_table = get_target_table()
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
    target_table = get_target_table()
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
    target_table = get_target_table()
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
    target_table = get_target_table()
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
    target_table = get_target_table()
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
    target_table = get_target_table()
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
    target_table = get_target_table()
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
    app.run(debug=True, dev_tools_prune_errors=False, threaded=False)


if __name__ == "__main__":
    main()
