import os
from flask import Flask, render_template
from . import auth
from . import interface


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.register_blueprint(auth.bp)
    app.register_blueprint(interface.bp)

    app.config.from_mapping(
        SECRET_KEY='key'
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    return app