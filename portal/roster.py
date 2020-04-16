from flask import render_template, Blueprint, session, g, flash, request, redirect

from . import db

bp = Blueprint("roster", __name__)


@bp.route('/courses/<int:course_id>/sessions/<int:session_id>/roster', methods=('GET', 'POST'))
def display_roster(course_id, session_id):

    if request.method == 'POST':

        email = request.form['email']
        already_enrolled = False
        error = None

        with db.get_db() as con:
            with con.cursor() as cur:

                # Find the student in the users table
                cur.execute("""SELECT id, name, email, role FROM users
                    WHERE email = %s""", (email,))

                user = cur.fetchone()

                # Check if the student is already in the current session
                if user:
                    cur.execute("""SELECT * FROM rosters
                        WHERE session_id = %s AND user_id = %s""",
                        (session_id, user['id'],))

                    if cur.fetchone():
                        already_enrolled = True

        # If there is no student with the entered email create an error message

        if user == None:

            error = 'No student found'

        # If the selected user is not a student, create an error message
        elif user['role'] != 'student':

            error = f'{user["name"]} is not a student'

        # If the student is already in the session create an error message
        elif already_enrolled:

            error = f'{user["name"]} is already enrolled in this session.'

        if error == None:

            with db.get_db() as con:
                with con.cursor() as cur:

                    cur.execute("""INSERT INTO rosters (user_id, session_id)
                        VALUES (%s, %s)""", (user['id'], session_id,))

        else:

            flash(error)

    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute('SELECT * FROM courses WHERE course_num = %s',
                (course_id,))

            course = cur.fetchone()

            cur.execute('SELECT * FROM sessions WHERE id = %s',
                (session_id,))

            session = cur.fetchone()

            cur.execute("""SELECT name, email, user_id FROM users JOIN rosters
                ON user_id = users.id
                WHERE session_id = %s""",
                (session_id,))

            students = cur.fetchall()


    return render_template('roster.html', course=course, session=session, students=students)
