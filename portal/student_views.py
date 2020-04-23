from flask import Blueprint, g, render_template
from . import db
from portal.auth import login_required, student_required
from portal import sessions, assign

bp = Blueprint("student_views", __name__)


# Page where students can view their schedules
@bp.route("/schedule", methods=('GET', 'POST'))
@login_required
@student_required
def view_schedule():
    """Students can view their schedule here"""

    # Here, I will put what goes into the schedule
    # In order, I am selecting the session name, location, room number,
    # days and time of day, a description, teacher name, and who is in
    # that session. I am selecting rosters.user_id because in schedule.html,
    # I am checking what courses the currently logged in student is enrolled in.
    cur = db.get_db().cursor()
    cur.execute("""
        SELECT sessions.session_name,
                sessions.id,
                sessions.location,
                sessions.room_number,
                sessions.times,
                courses.description,
                users.name,
                rosters.user_id
        FROM sessions
        INNER JOIN courses ON courses.course_num = sessions.course_id
        INNER JOIN users ON courses.teacher_id = users.id
        INNER JOIN rosters ON sessions.id = rosters.session_id
        WHERE courses.major_id = %s""",
        (g.user['major_id'],)
        )
    infos = cur.fetchall()

    cur.close()

    return render_template("layouts/student_views/schedule.html", infos=infos)

@bp.route("/your_assignments/session/<int:session_id>", methods=('GET', 'POST'))
@login_required
@student_required
def session_assignments(session_id):
    """Allows students to view their assignments for a specific course"""
    session = sessions.get_session(session_id)
    cur = db.get_db().cursor()
    cur.execute("""
            SELECT * FROM assignments
            WHERE sessions_id = %s""",
            (session_id,))
    assignments = cur.fetchall()
    cur.close()
    return render_template("layouts/student_views/your_assignments.html", session=session, assignments=assignments)


@bp.route("/session/<int:session_id>/assignment_details/<int:assign_id>", methods=('GET', 'POST'))
@login_required
@student_required
def assign_view(assign_id, session_id):
    """Allows students to view a specific assignment's details for a specific course"""
    assignment = assign.get_assignment(assign_id)
    session = sessions.get_session(session_id)
    return render_template("layouts/student_views/assignment_details.html", session=session, assignment=assignment)
