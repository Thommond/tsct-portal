from flask import redirect, g, url_for, render_template, session, request, Blueprint, flash, abort
import functools
from . import db
from portal.auth import login_required, teacher_required

bp = Blueprint("courses", __name__)


@bp.route("/courses", methods=('GET', 'POST'))  # Management Page
@login_required
@teacher_required
def course_manage():
    """Allows teachers to have a page which allows
    them to edit and create courses"""

    cur = db.get_db().cursor()
    cur.execute('SELECT * FROM courses')
    courses = cur.fetchall()

    cur.close()

    return render_template("layouts/courses/courseMan.html", courses=courses)


@bp.route("/courses/create", methods=('GET', 'POST'))  # Course Create
@login_required
@teacher_required
def course_create():
    """Allows the teacher to create a course
    and fill out specifics on course"""
    all_majors = get_majors()

    if request.method == 'POST':

        course_number = request.form['courseNumber']
        course_title = request.form['courseTitle']
        course_description = request.form['description']
        course_credit = request.form['courseCredits']
        course_major = request.form['major_name']
        error = None
        result = isinstance(course_major, int)

        # Checks if course_number is a number
        try:
            int(course_number)
        except ValueError:
            error = 'Course number needs to be a number'

        # Checks if course_credit is a number
        try:
            int(course_credit)
        except ValueError:
            error = 'Credit amount needs to be a number'

        # Checks if course_major is a number
        try:
            int(course_major)
        except ValueError:
            error = 'Major not found'

        # Checks if the selected major is in the database
        if not error:
            with db.get_db() as con:
                with con.cursor() as cur:

                    cur.execute('SELECT * FROM majors WHERE id = %s', (course_major,))

                    check_major = cur.fetchone()

                    if check_major == None:

                        error = 'Major not found'
        if not course_number:
            error = 'Course number is required'
        if not course_title:
            error = 'Title of course is required'
        if not course_credit:
            error = 'Credit amount is required'
        if not course_major:
            error = 'Major is required'

        if error is None:
            with db.get_db() as con:
                with con.cursor() as cur:
                    # Adds info to courses table
                    cur.execute("""INSERT INTO courses (course_num, course_title, description,
                    credits, major_id, teacher_id)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                            (course_number, course_title, course_description,
                             course_credit, course_major, g.user['id'], )
                            )
                    con.commit()

                    return redirect(url_for("courses.course_manage"))

        flash(error)

    return render_template('layouts/courses/courseCreate.html', all_majors=all_majors)


# Needs new template
@bp.route("/courses/<int:course_id>/edit", methods=('GET', 'POST'))
@login_required
@teacher_required


def course_edit(course_id):
    """Allows teachers to edit the course"""
    course = get_course(course_id)
    if g.user['id'] != course['teacher_id']:
        abort(403)
    if request.method == "POST":

        credit = request.form['editCredit']
        title = request.form['editTitle']
        desc = request.form['editDesc']
        error = None

        # Checks if course_credit is a number
        try:
            int(credit)
        except ValueError:
            error = 'Credit amount needs to be a number'

        if not credit:
            error = 'Credit amount is required'
        if not title:
            error = 'Title of course is required'

        if error is None:

            with db.get_db() as con:
                with con.cursor() as cur:

                    cur.execute("""UPDATE courses SET
                    course_title = %s,
                    description = %s,
                    credits = %s
                    WHERE course_num = %s
                    """,
                                (title, desc, credit, course_id,)
                                )
                    con.commit()

                    return redirect(url_for("courses.course_manage"))

        flash(error)

    return render_template("layouts/courses/courseEdit.html", course=course)


def get_course(course_id):
    """Gets the course from the database"""
    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute(
                'SELECT course_num, credits, description, course_title, teacher_id'
                ' FROM courses WHERE course_num = %s',
                (course_id,))

            course = cur.fetchone()

            if course is None:
                abort(404)

            return course


def get_majors():
    """Gets the list of majors"""
    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute(
                'SELECT name, id '
                'FROM majors'
            )

            all_majors = cur.fetchall()

            return all_majors
