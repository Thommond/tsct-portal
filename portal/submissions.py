from flask import (
    render_template, Blueprint, session, g, flash, request, redirect, url_for, abort
)

from . import db, auth

bp = Blueprint("submissions", __name__)

@bp.route('/course/<int:course_id>/session/<int:session_id>/assignments/<int:assignment_id>/submissions')
@auth.login_required
@auth.teacher_required
def submission_list(course_id, session_id, assignment_id):
    """Returns a page with a list of all submissions for an assignment that
    only the teacher can see"""

    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute('SELECT * FROM sessions WHERE id = %s', (session_id,))

            session = cur.fetchone()

            if session:

                cur.execute('SELECT * FROM courses WHERE course_num = %s', (session['course_id'],))

                course = cur.fetchone()

                cur.execute('SELECT * FROM rosters WHERE session_id = %s', (session['id'],))

                students = cur.fetchall()

            cur.execute('SELECT * FROM assignments WHERE id = %s', (assignment_id,))

            assignment = cur.fetchone()


    # Security Checks
    if session == None or assignment == None:

        abort(404)

    if course['teacher_id'] != g.user['id']:

        abort(403)

    if assignment['sessions_id'] != session['id']:

        abort(403)

    # Create a record in submissions for every student in the session
    # who does not already have one
    # (This may not be necessary once students are able to submit assignments themselves)
    for student in students:

        with db.get_db() as con:
            with con.cursor() as cur:

                cur.execute('SELECT * FROM submissions WHERE student_id = %s AND assignment_id = %s',
                    (student['user_id'], assignment['id'],))

                if cur.fetchone() == None:

                    cur.execute("""INSERT INTO submissions (assignment_id, student_id)
                                   VALUES (%s, %s)""", (assignment['id'], student['user_id'],))

    # Retrieve all of the submissions for the assignment
    with db.get_db() as con:
        with con.cursor() as cur:

            # Each submission has it's id and its student's name
            cur.execute("""SELECT s.id, u.name
                FROM submissions s JOIN users u ON s.student_id = u.id
                WHERE assignment_id = %s""", (assignment['id'],))

            submissions = cur.fetchall()


    return render_template('submissions/submissions.html', submissions=submissions, assignment=assignment, session=session)


@bp.route('/course/<int:course_id>/session/<int:session_id>/assignments/<int:assignment_id>/submissions/<int:submission_id>', methods=('GET', 'POST'))
@auth.login_required
@auth.teacher_required
def grade_submission(course_id, session_id, assignment_id, submission_id):
    """Handles the page where a teacher can enter a grade + feedback for a
    student's submission"""

    with db.get_db() as con:
        with con.cursor() as cur:
            # Retrieve all of the necessary attributes from the database

            cur.execute('SELECT id, course_id FROM sessions WHERE id = %s', (session_id,))

            session = cur.fetchone()

            if session:

                cur.execute('SELECT teacher_id FROM courses WHERE course_num = %s', (session['course_id'],))

                course = cur.fetchone()

            cur.execute('SELECT * FROM assignments WHERE id = %s', (assignment_id,))

            assignment = cur.fetchone()

            cur.execute('SELECT * FROM submissions WHERE id = %s', (submission_id,))

            submission = cur.fetchone()

            if submission:
                cur.execute('SELECT name FROM users WHERE id = %s', (submission['student_id'],))

                student = cur.fetchone()

    # Securtiy Checks
    if course['teacher_id'] != g.user['id']:

        abort(403)

    if submission == None or assignment == None or session == None:

        abort(404)

    if assignment['sessions_id'] != session['id']:

        abort(403)

    if submission['assignment_id'] != assignment['id']:

        abort(403)

    if request.method == 'POST':

        grade = request.form['grade']
        feedback = request.form['feedback']
        error = None
        success_message = None

        # Check that grade is a number
        try:
            int(grade)
        except ValueError:
            error = 'Grade needs to be a number'

        # Insert grade + feedback into the appropriate submission
        if error == None:

            with db.get_db() as con:
                with con.cursor() as cur:

                    cur.execute("""UPDATE submissions
                        SET grade = %s,
                            feedback = %s
                        WHERE id = %s""", (grade, feedback, submission['id']))

                    con.commit()

                    # Retrieve the updated submission info
                    cur.execute('SELECT * FROM submissions WHERE id = %s', (submission_id,))
                    submission = cur.fetchone()

                    success_message = 'Grade Entered'


        if error != None:
            flash(error, 'flash')

        if success_message != None:
            flash(success_message, 'success')

    return render_template('submissions/feedback.html', assignment=assignment, student=student['name'], session=session, submission=submission)


def letter_grade(points, total):
    """Given an amount of points and the total points availage,
    returns the corresponding letter grade for the average"""
    # letter_grade(9, 10) returns 'A'

    avg = (points / total) * 100

    # more specific grades (B-, C+, etc.) can be added to scale,
    # as long as it remains in ascending order (low to high)
    scale = [
        (60, 'D-'),
        (64, 'D'),
        (67, 'D+'),
        (70, 'C-'),
        (74, 'C'),
        (77, 'C+'),
        (80, 'B-'),
        (84, 'B'),
        (87, 'B+'),
        (90, 'A-'),
        (94, 'A'),
        (97, 'A+')
    ]
    # Grade is F defualt
    grade = 'F'

    for value in scale:
        if avg >= value[0]:
            grade = value[1]

    return grade
