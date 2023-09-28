"""
This script creates and runs the Flask application for the Wesnoth MP Database Dashboard.
This is used to start the production server. For development, use `python app.py` instead.

Usage:

    `gunicorn --bind :$PORT main:server`

Where $PORT specifies the port number

Note: Gunicorn only runs on Linux/Unix systems. For Windows, use `waitress` instead, or use a Linux container/VM to run Gunicorn.
"""

from app import create_app

app = create_app()
server = app.server
