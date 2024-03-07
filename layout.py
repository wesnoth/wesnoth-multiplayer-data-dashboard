import json

import dash
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

    with open("config.json", "r") as f:
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
        use_pages=True,
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

    layout = html.Div(
        id="top-level-container",
        children=[
            html.Div(
                id="title-container",
                children=[
                    html.Div(
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
                    html.Nav(
                        id="navbar",
                        children=[
                            html.Ul(
                                id="nav-list",
                                children=[
                                    html.Li(dcc.Link("Statistics", href="/dashboard/")),
                                    html.Li(dcc.Link("Query", href="/dashboard/query")),
                                ]
                            )
                        ],
                    )
                ],
            ),
            dash.page_container,
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
