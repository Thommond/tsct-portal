from flask import abort, Blueprint, g, render_template, session
from portal.auth import login_required, teacher_required
from . import sessions, courses, db

bp = Blueprint("teacher_views", __name__)

# Page where teachers can view students' grades for an assignment
@bp.route("/course/<int:course_id>/session/<int:sessions_id>/assignments/grades/<int:assign_id>/")
@login_required
@teacher_required

def assign_view(course_id, sessions_id, assign_id):
    course = courses.get_course(course_id)
    session = sessions.get_session(sessions_id)
    assignment = get_assignment(assign_id)

    if g.user['id'] != course['teacher_id']:
        abort(403)

    if course['course_num'] != session['course_id']:
        abort(403)

    if session['id'] != assignment['sessions_id']:
        abort(403)

    with db.get_db() as con:
        with con.cursor() as cur:
            # I need student name and grade (points, for now)
            cur.execute("""
                SELECT assignments.points, users.name
                FROM assignments, users
                WHERE users.role='student' AND assignments.id=%s""",
                (assign_id,)
                )
            grades = cur.fetchall()
            cur.execute("""
                SELECT assign_name, description
                FROM assignments
                WHERE id=%s""",
                (assign_id,)
                )
            info = cur.fetchone()
    return render_template('layouts/teacher_view/assign_grades.html', grades=grades, info=info, session=session)

def get_assignment(assign_id):
    """Gets the assignment from the database"""
    with db.get_db() as con:
        with con.cursor() as cur:
            cur.execute(
                'SELECT id, assign_name, description, points, sessions_id, due_time'
                ' FROM assignments WHERE id = %s',
                (assign_id, )
            )
            assign = cur.fetchone()

            if assign is None:
                abort(404)

            return assign
