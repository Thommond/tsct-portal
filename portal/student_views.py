from flask import abort, Blueprint, g, render_template
from . import db
from portal.auth import login_required, student_required
from portal import sessions, assign, courses

bp = Blueprint("student_views", __name__)


# Page where students can view their schedules
@bp.route("/schedule", methods=('GET', 'POST'))
@login_required
@student_required
def view_schedule():
    """Students will have the ability to view session and course
    information from this template route"""


    cur = db.get_db().cursor()
    # Getting all needed info for schedule from database
    cur.execute("""
        SELECT sessions.session_name,
                sessions.course_id,
                sessions.id,
                sessions.location,
                sessions.room_number,
                sessions.times,
                courses.description,
                courses.course_num,
                users.name,
                rosters.user_id
        FROM sessions
        INNER JOIN courses ON courses.course_num = sessions.course_id
        INNER JOIN users ON courses.teacher_id = users.id
        INNER JOIN rosters ON sessions.id = rosters.session_id
        WHERE rosters.user_id = %s""",
        (g.user['id'],)
        )

    infos = cur.fetchall()

    cur.close()

    return render_template("student_views/schedule.html", infos=infos)

@bp.route("/course/<int:course_id>/session/<int:session_id>/your_assignments", methods=('GET', 'POST'))
@login_required
@student_required
def session_assignments(session_id, course_id):
    """Allows students to view their assignments for a specific course"""
    session = sessions.get_session(session_id)
    course = courses.get_course(course_id)

    if session['course_id'] != course['course_num']:
        abort(403)

    cur = db.get_db().cursor()
    
    cur.execute("""
            SELECT * FROM assignments
            WHERE sessions_id = %s""",
            (session_id,))

    assignments = cur.fetchall()

    cur.close()
    return render_template("student_views/your_assignments.html", session=session, assignments=assignments, course=course)


@bp.route("/course/<int:course_id>/session/<int:session_id>/assignment_details/<int:assign_id>", methods=('GET', 'POST'))
@login_required
@student_required
def assign_view(assign_id, session_id, course_id):
    """Allows students to view a specific assignment's details for a specific course"""
    assignment = assign.get_assignment(assign_id)
    session = sessions.get_session(session_id)
    course = courses.get_course(course_id)
    if session['course_id'] != course['course_num']:
        abort(403)
    if session['id'] != assignment['sessions_id']:
        abort(403)

    return render_template("student_views/assignment_details.html", session=session, assignment=assignment, course=course)

@bp.route("/course/<int:course_id>/session/<int:session_id>/grades", methods=('GET', 'POST'))
@login_required
@student_required
def grade_book(session_id, course_id):
    session = sessions.get_session(session_id)
    course = courses.get_course(course_id)
    assignments = assign.get_assignment(session_id, True)
    for assignment in assignments:
        with db.get_db() as con:
            with con.cursor() as cur:
                cur.execute('SELECT * FROM submissions WHERE student_id = %s AND assignment_id = %s',
                    (g.user['id'], assignment['id'],))

                if cur.fetchone() == None:
                    cur.execute("""INSERT INTO submissions (assignment_id, student_id)
                            VALUES (%s, %s)""", (assignment['id'], g.user['id'],))



    submissions = get_submissions(session_id)
    """Allows student to veiw grades for a course"""
    if session['course_id'] != course['course_num']:
        abort(403)

    for submission in submissions:
        if submission['grade'] == None:
            submission['grade'] = 0

    return render_template("student_views/grade_book.html", course=course, session=session, submissions=submissions)

def get_submissions(session_id):
    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute("""SELECT assignments.assign_name,
                            assignments.id, assignments.points, submissions.id, submissions.student_id,
                            submissions.grade, submissions.feedback, submissions.assignment_id
                            FROM assignments
                            INNER JOIN submissions ON assignments.id = submissions.assignment_id
                            WHERE assignments.sessions_id = %s AND submissions.student_id = %s
                            """,(session_id, g.user['id'], ))

            return cur.fetchall()
