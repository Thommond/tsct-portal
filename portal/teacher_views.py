from flask import abort, Blueprint, g, render_template
from . import db
from portal.auth import login_required, teacher_required
from portal import sessions, assign, courses, submissions

bp = Blueprint("teacher_views", __name__)

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
        print(student)
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
                print(assignments)
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
