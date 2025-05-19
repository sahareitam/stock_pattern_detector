# api/__init__.py
from api.app import flask_app, run_api, create_app

# Export the main functions and objects
__all__ = ['flask_app', 'run_api', 'create_app']