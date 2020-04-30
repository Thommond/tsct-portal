import os

from flask import Flask, render_template, abort

from werkzeug.security import check_password_hash, generate_password_hash

##########################
####Custom Error Pages####
##########################
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("500.html", e=e), 500


def forbidden(e):
    """Notifies the user that the previous action they attempted is not allowed."""
    return render_template('errors/403.html'), 403

def page_not_found(e):
    """Tells the user what they are looking for is not there."""
    return render_template('errors/404.html'), 404

def gone(e):
    """Notifies the user the resource they are looking for is no longer here"""
    return render_template('errors/410.html'), 410

def bad_request(e):
    """Notifies the user that the request they have attempted is not excepted"""
    return render_template('errors/400.html'), 400
########################

def create_app(test_config=None):
    """Factory to configure and return a Flask application.
    Keyword arguments:
    test_config -- dictionary to configure the app for tests (default None)
    """

    # Create the Flask application object using this module's name
    app = Flask(__name__, instance_relative_config=True)
    # Registering the auto-matic error pages
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, forbidden)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(500, handle_exception)
    app.register_error_handler(410, gone)

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
    # --------------
    from . import courses
    app.register_blueprint(courses.bp)

    # Assignement Routes
    # --------------
    from . import assign
    app.register_blueprint(assign.bp)

    # Sessions Routes
    # --------------
    from . import sessions
    app.register_blueprint(sessions.bp)

    # Register Routes
    # ---------------
    from . import auth
    app.register_blueprint(auth.bp)
    # Roster Routes
    # ---------------
    from . import roster
    app.register_blueprint(roster.bp)

    #Submission Route
    from . import submissions
    app.register_blueprint(submissions.bp)

    # Student View Routes
    # -------------------
    from . import student_views
    app.register_blueprint(student_views.bp)

    # Teacher View Routes
    # -------------------
    from . import teacher_views
    app.register_blueprint(teacher_views.bp)


    @app.route('/')
    @auth.login_required
    def index():
        return render_template('index.html')



    # Return application object to be used by a WSGI server, like gunicorn
    return app
