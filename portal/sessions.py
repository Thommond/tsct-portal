from flask import redirect, g, url_for, render_template, session, request, Blueprint, flash, abort
import functools
from . import courses
from . import db
from portal.auth import login_required, teacher_required

bp = Blueprint("sessions", __name__)

@bp.route("/courses/<int:course_id>/sessions/<int:sessions_id>/edit", methods=('GET', 'POST'))
@login_required
@teacher_required

def session_edit(course_id, sessions_id):
    """Allows teachers to edit a specific session of a
    specific course"""
    session = get_session(sessions_id)
    course = courses.get_course(session['course_id'])
    if g.user['id'] != course['teacher_id']:
        abort(403)

    if course['course_num'] != session['course_id']:
        abort(403)

    if request.method == 'POST':

        name = request.form['editName']
        times = request.form['editTimes']
        room = request.form['editRoom']
        location = request.form['editLocal']
        error = None

        if not name:
            error = 'Required field missing.'
        if not times:
            error = 'Required field missing.'
        if not room:
            error = 'Required field missing.'
        if not location:
            error = 'Required field missing.'

        with db.get_db() as con:
            with con.cursor() as cur:

                if error is None:

                    cur.execute("""UPDATE sessions SET
                        session_name = %s,
                        times = %s,
                        room_number = %s,
                        location = %s
                        WHERE id = %s AND course_id = %s
                        """,
                        (name, times, room, location, sessions_id, course['course_num'], )
                        )
                    con.commit()

                    return redirect(url_for( 'sessions.session_manage', course_id=course['course_num']))

        flash(error)


    return render_template("sessions/editSession.html", course=course, session=session)


@bp.route("/courses/<int:course_id>/sessions/create", methods=('GET','POST'))
@login_required
@teacher_required
def session_create(course_id):
    """Allows a teacher to create a speficic session in  a
    specific course"""
    course = courses.get_course(course_id)
    students = get_students()
    if g.user['id'] != course['teacher_id']:
        abort(403)



    if request.method == 'POST':

        title = request.form['sessionTitle']
        times = request.form['sessionTimes']
        room = request.form['roomNumber']
        location = request.form['locations']
        error = None

        if not title:
            error = 'Required field missing.'
        if not times:
            error = 'Required field missing.'
        if not room:
            error = 'Required field missing.'
        if not location:
            error = 'Required field missing.'

        with db.get_db() as con:
            with con.cursor() as cur:

                if error is None:

                    cur.execute("""INSERT INTO sessions (times, session_name, room_number, location, course_id)
                        VALUES (%s, %s, %s, %s, %s )
                    """,
                    (times, title, room, location, course_id, )
                    )
                    con.commit()

                    return redirect(url_for("sessions.session_manage", course_id=course['course_num']))

                flash(error)

    return render_template("sessions/createSession.html", course=course)


@bp.route("/courses/<int:course_id>/sessions", methods=('GET', 'POST'))
@login_required
@teacher_required
def session_manage(course_id):
    """The management page of all the sessions in
    a specific course"""

    course = courses.get_course(course_id)
    if g.user['id'] != course['teacher_id']:
        abort(403)

    cur = db.get_db().cursor()
    cur.execute('SELECT * FROM sessions WHERE course_id = %s',
    (course_id, ))

    sessions = cur.fetchall()

    cur.close()

    return render_template("sessions/sessionManage.html", course=course, sessions=sessions)

def get_session(sessions_id):
    """Gets the session from the database"""
    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute(
                'SELECT id, times, session_name, room_number, location, course_id'
                ' FROM sessions WHERE id = %s',
                (sessions_id, )
            )

            session = cur.fetchone()

            if session is None:
                abort(404)

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
