from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)

import functools
from . import db
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Renders the login page.
    Starts a new session if a login attempt is successful."""

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute('SELECT * FROM users WHERE email = %s', (email,))
                user = cur.fetchone()



        error = None

        # Check for empty email form
        if not email:
            error = 'Enter an email'

        # Check for empty password form
        elif not password:
            error = 'Enter a password'

        # Check if entered password matches the password in the database
        elif not user or not check_password_hash(user['password'], password):
            error = 'Incorrect email or password'


        # If no errors occured, start a new session
        if error == None:

            session.clear()
            session['user_id'] = user['id']

            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')


@bp.route('/logout')
def logout():
    """Clears the current session"""
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_user():
    """Checks if the user is logged in before every request to the server.
    If they are, pull their data out of the database and put it in g.user"""

    user_id = session.get('user_id')

    # Check if the user has an active session
    if user_id is None:
        g.user = None
    else:
        # Pull the user's data out of the database and assign it to g
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
                g.user = cur.fetchone()


def login_required(view):
    """Checks if the user is logged in, and if not, redirects them to the login page"""
    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped


def teacher_required(view):
    """Checks if the logged in user is a teacher"""
    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user['role'] != 'teacher':
            abort(403)

        return view(**kwargs)

    return wrapped

def student_required(view):
    """Checks if the logged in user is a student"""
    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user['role'] != 'student':
            return redirect(url_for('index'))

        return view(**kwargs)
    return wrapped
