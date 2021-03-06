# -*- coding: utf-8 -*-

import os

from flask import Flask, request, render_template
#from flask.ext.babel import Babel

from .config import DefaultConfig
from .extensions import db


from .shai import shai
from .user import user
from .api import api
from .manage import manage


# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = (
    shai,
    user,
    api,
    manage,
)

def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    app_name = DefaultConfig.PROJECT
    blueprints = DEFAULT_BLUEPRINTS

    #app = Flask(app_name, instance_path=INSTANCE_FOLDER_PATH, instance_relative_config=True)
    app = Flask(app_name)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_logging(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    # http://flask.pocoo.org/docs/config/#instance-folders
    #app.config.from_pyfile('production.cfg', silent=True)

    if config:
        app.config.from_object(config)



def configure_extensions(app):
    # flask-sqlalchemy
    db.init_app(app)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_template_filters(app):
    pass


def configure_logging(app):
    """Configure file(info) and email(error) logging."""

    if app.debug or app.testing:
        # Skip debug and test mode. Just check standard output.
        return

    import logging

    # Set info level on logger, which might be overwritten by handers.
    # Suppress DEBUG messages.
    app.logger.setLevel(logging.INFO)

    info_log = os.path.join(app.config['LOG_FOLDER'], 'info.log')
    info_file_handler = logging.handlers.RotatingFileHandler(info_log, maxBytes=100000, backupCount=10)
    info_file_handler.setLevel(logging.INFO)
    info_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.addHandler(info_file_handler)



def configure_hook(app):
    @app.before_request
    def before_request():
        pass


def configure_error_handlers(app):

    """@app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/forbidden_page.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/page_not_found.html"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/server_error.html"), 500"""
    pass
