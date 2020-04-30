from flask import abort, Blueprint, g, render_template
from . import db
from portal.auth import login_required, teacher_required
from portal import sessions, assign, courses, submissions

bp = Blueprint("teacher_views", __name__)

# Page where teachers can view students' grades for an assignment
@bp.route("/course/<int:course_id>/session/<int:sessions_id>/assignments/<int:assign_id>/grades")
@login_required
@teacher_required

def assign_grade(course_id, sessions_id, assign_id):
    course = courses.get_course(course_id)
    session = sessions.get_session(sessions_id)
    students = get_students(sessions_id)
    assignment = assign.get_assignment(assign_id)
    students_assign_grade = []

    if g.user['id'] != course['teacher_id']:
        abort(403)

    if course['course_num'] != session['course_id']:
        abort(403)

    if session['id'] != assignment['sessions_id']:
        abort(403)

    for student in students:
        # default of zero
        points = 0
        grades = 0

        with db.get_db() as con:
            with con.cursor() as cur:

            # Getting each assignment data
                cur.execute(
                """SELECT assign_name, id, points, description
                FROM assignments WHERE sessions_id = %s AND id = %s""",
                (student['id'], assign_id,)
                )
                # all assignments per student
                assignment = cur.fetchone()

                # All grades per student's assignment
                cur.execute("""
                    SELECT grade
                    FROM submissions
                    WHERE student_id = %s AND assignment_id = %s""",
                    (student['user_id'], assign_id,))
                student_submission = cur.fetchone()

                # If there is no submission, set a default grade of zero
                if student_submission[0] == None:
                    student_submission[0] = 0

                letter_grade = submissions.letter_grade(student_submission[0], assignment['points'])
                one_assignment_grade = (student['name'], student_submission, letter_grade)
                # Adding submission to list
                students_assign_grade.append(one_assignment_grade)
    return render_template('layouts/teacher_view/assign_grades.html', students=students, session=session, assignment=assignment, assignment_grade=students_assign_grade)


@bp.route('/course/<int:course_id>/session/<int:sessions_id>/all_grades', methods=('GET', 'POST'))
@login_required
@teacher_required
def all_grades(course_id, sessions_id):
    """Teachers can view all of their students total
    grades with in a class session"""
    course = courses.get_course(course_id)
    session = sessions.get_session(sessions_id)
    students = get_students(sessions_id)
    # Holds all total grades
    total_student_grades = []


    if g.user['id'] != course['teacher_id']:
        abort(403)

    if course['course_num'] != session['course_id']:
        abort(403)

    for student in students:
        # default of zero
        points = 0
        grades = 0

        with db.get_db() as con:
            with con.cursor() as cur:

            # Getting each assignment data
                cur.execute(
                """SELECT assign_name, id, points
                FROM assignments WHERE sessions_id = %s""",
                (student['id'], )
                )
                # all assignments per student
                assignments = cur.fetchall()
                for assignment in assignments:

                    if assignment['points'] != None:
                        points += assignment['points']


                cur.execute(
                """SELECT grade, assignment_id, student_id FROM Submissions
                WHERE student_id = %s""",
                (student['user_id'], )
                )

                student_submissions = cur.fetchall()

                for submission in student_submissions:


                    if submission['grade'] != None:
                        grades += submission['grade']


                total_student_grade = submissions.letter_grade(grades, points)
                # adding each student total grade to the list

                grade_and_name = (total_student_grade, student['name'])

                total_student_grades.append(grade_and_name)


    return render_template("teacher_views/allGrades.html", course=course, session=session, letter_grade=total_student_grades, students=students)



def get_students(sessions_id):
    """Gets all the students in a session"""
    with db.get_db() as con:
        with con.cursor() as cur:

            cur.execute(
            # Get all students in session
            """SELECT sessions.course_id,
                      sessions.id,
                      courses.course_num,
                      users.name,
                      rosters.user_id,
                      rosters.session_id
                FROM users
                INNER JOIN rosters ON rosters.user_id = users.id
                INNER JOIN sessions ON sessions.id = rosters.session_id
                INNER JOIN courses ON courses.course_num = sessions.course_id
                WHERE session_id = %s """,
                (sessions_id, )
            )

            students = cur.fetchall()



            return students
