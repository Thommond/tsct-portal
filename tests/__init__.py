import os

from flask import Flask, render_template, g

from werkzeug.security import check_password_hash, generate_password_hash

def create_app(test_config=None):
    """Factory to configure and return a Flask application.
    Keyword arguments:
    test_config -- dictionary to configure the app for tests (default None)
    """

    # Create the Flask application object using this module's name
    app = Flask(__name__, instance_relative_config=True)

    # Configure App
    # -------------
    # Default configuration, can be overwritten by specific environment
    app.config.from_mapping(
        SECRET_KEY='gordu4rc1&zsi!uxff!d6e+k#1405$qjh-81k8y@3lbv_%04#(',
        DB_URL="postgresql://portal_user@localhost/portal",
        DB_SSLMODE="allow",
    )

    if test_config is None:
        # App configuration for dev or prod if `config.py` exists
        app.config.from_pyfile("config.py", silent=True)

        # Check for environment variables on Heroku
        prod_db_url = os.environ.get("DATABASE_URL", None)
        if prod_db_url is not None:
            app.config.from_mapping(
                DB_URL=prod_db_url,
                DB_SSLMODE="require"
            )
    else:
        # App configuration specifically for tests
        app.config.from_mapping(test_config)

    # Setup Database
    # --------------
    from . import db
    db.init_app(app)
    # Teacher Course Editor routes
    # ---------------
    from . import course_editor
    app.register_blueprint(course_editor.bp)


    # Register Routes
    # ---------------
    from . import auth
    app.register_blueprint(auth.bp)

    @app.route('/')
    @auth.login_required
    def index():
        return render_template('index.html')

    # Return application object to be used by a WSGI server, like gunicorn
    return app
