"""
This script creates and runs the Flask application for the Wesnoth MP Database Dashboard.

Usage:

    `gunicorn --bind :$PORT main:server`

Where $PORT specifies the port number

Note: Gunicorn only runs on Linux/Unix systems. For Windows, use `waitress` instead.
"""

from app import create_app

app = create_app()
server = app.server
