import json

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html


def create_app():
    """
    Creates a Dash web application instance for the Wesnoth Multiplayer Dashboard.

    This function initializes a Dash web application instance with external stylesheets,
    meta tags, and a layout tailored for displaying Wesnoth multiplayer game data.

    Returns:
        Dash: A Dash web application instance.
    """

    with open(".config/config.json", "r") as f:
        config = json.load(f)
        url_base_pathname = config["url_base_pathname"]

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
        url_base_pathname=url_base_pathname,
    )

    app.layout = create_app_layout()
    return app


def create_app_layout():
    """
    Creates the layout for the Wesnoth Multiplayer Dashboard web application.

    This function defines the structure of the dashboard's user interface, including
    the title, user guide modal, date picker, data table, charts, and footer.

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
                            href="https://github.com/wesnoth/wesnoth-multiplayer-data-dashboard",
                            target="_blank",
                        ),
                    ],
                ),
            ),
        ],
    )
    return layout
