from flask import redirect, g, url_for, render_template, session, request, Blueprint, flash, abort
import functools
from . import course_editor
from . import db
from portal.auth import login_required, teacher_required

bp = Blueprint("session_editor", __name__)

@bp.route("/courses/<int:course_id>/sessions/<int:sessions_id>/edit", methods=('GET', 'POST'))
@login_required
@teacher_required
def session_edit(course_id, sessions_id):
    """Allows teachers to edit a specific session of a
    specific course"""
    course = course_editor.get_course(course_id)
    session = get_session(sessions_id)
    if g.user['id'] != course['teacher_id']:
        return redirect(url_for('index'))

    if request.method == 'POST':

        name = request.form['editName']
        times = request.form['editTimes']
        room = request.form['editRoom']
        location = request.form['editLocal']
        error = None

        with db.get_db() as con:
            with con.cursor() as cur:

                if error is None:

                    cur.execute("""UPDATE sessions SET
                        name = %s,
                        times = %s,
                        room_number = %s,
                        location = %s
                        WHERE id = %s AND course_id = %s
                        """,
                        (name, times, room, location, sessions_id, course_id, )
                        )
                    con.commit()

                    return redirect(url_for( 'session_editor.session_manage', id=course['course_num']))

                flash(error)


    return render_template("layouts/editSession.html", course=course, session=session)


@bp.route("/courses/<int:id>/sessions/create", methods=('GET','POST'))
@login_required
@teacher_required
def session_create(id):
    """Allows a teacher to create a speficic session in  a
    specific course"""
    course = course_editor.get_course(id)
    students = get_students()
    if g.user['id'] != course['teacher_id']:
        return redirect(url_for('index'))



    if request.method == 'POST':

        title = request.form['sessionTitle']
        times = request.form['sessionTimes']
        room = request.form['roomNumber']
        location = request.form['locations']
        error = None

        with db.get_db() as con:
            with con.cursor() as cur:

                if not title:
                    error = 'Required field missing.'
                if not times:
                    error = 'Required field missing.'
                if not room:
                    error = 'Required field missing.'
                if not location:
                    error = 'Required field missing.'

                if error is None:

                    cur.execute("""INSERT INTO sessions (times, name, room_number, location, course_id)
                        VALUES (%s, %s, %s, %s, %s )
                    """,
                    (times, title, room, location, id, )
                    )
                    con.commit()

                    return redirect(url_for("session_editor.session_manage", id=course['course_num']))

                flash(error)

    return render_template("layouts/createSession.html", course=course)


@bp.route("/courses/<int:id>/sessions", methods=('GET', 'POST'))
@login_required
@teacher_required
def session_manage(id):
    """The management page of all the sessions in
    a specific course"""

    course = course_editor.get_course(id)
    if g.user['id'] != course['teacher_id']:
        return redirect(url_for('index'))

    cur = db.get_db().cursor()
    cur.execute('SELECT * FROM sessions WHERE course_id = %s',
    (id, ))

    sessions = cur.fetchall()

    cur.close()

    return render_template("layouts/sessionManage.html", course=course, sessions=sessions)


def get_session(sessions_id):
    """Gets the session from the database"""
    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute(
                'SELECT id, times, name, room_number, location, course_id'
                ' FROM sessions WHERE id = %s',
                (sessions_id, )
            )

            session = cur.fetchone()

            if session is None:
                abort(404, "Session id {0} doesn't exist.".format(sessions_id))

            return session

def get_students():
    """Gets all the students from the database"""
    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute(
            'SELECT id, name, major_id, email, password, role'
            " FROM users WHERE role = 'student'"
            )

            students = cur.fetchall()

            return students
