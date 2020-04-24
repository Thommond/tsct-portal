import pytest
from portal.student_views import view_schedule
from .test_courses import login, logout

# I need to verify that there is a connection to the database
#
# For the render_template line, check for something that should always be on the
# schedule page, like "Schedule" or "Title", something like that
#

def test_schedule_view(client):
    assert client.get('/schedule').status_code == 302
    # login to check database
    rv = login(client, 'student@stevenscollege.edu', 'asdfgh')
    assert b'Logged in' in rv.data
    # go to schedule view to test data on page
    assert client.get('/schedule').status_code == 200
    response = client.get('/schedule')
    # test to see if mock data is on page, and see if the location/url is correct
    assert b'Teacher Name' in response.data
    assert b'Ms.Sullivan' in response.data
    # test logging out
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

def test_session_assignments(client):
    assert client.get('/course/216/session/1/your_assignments').status_code == 302
    # login to check database
    rv = login(client, 'student@stevenscollege.edu', 'asdfgh')
    assert b'Logged in' in rv.data
    # go to schedule view to test data on page
    assert client.get('/course/216/session/1/your_assignments').status_code == 200
    response = client.get('/course/216/session/1/your_assignments')
    # test to see if mock data is on page, and see if the location/url is correct
    assert b'Your Assignments' in response.data
    assert b'test1' in response.data
    # test logging out
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

def test_assign_view(client):
    assert client.get('/course/216/session/1/assignment_details/2').status_code == 302
    # login to check database
    rv = login(client, 'student@stevenscollege.edu', 'asdfgh')
    assert b'Logged in' in rv.data
    # go to schedule view to test data on page
    assert client.get('/course/216/session/1/assignment_details/2').status_code == 200
    response = client.get('/course/216/session/1/assignment_details/2')
    # test to see if mock data is on page, and see if the location/url is correct
    assert b'Title' in response.data
    assert b'test1' in response.data
    # test logging out
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

def test_grades(client):
    """Test the grade_book page to see if page loades"""
    assert client.get('/course/180/session/2/grades').status_code == 302

    rv = login(
        client, 'student@stevenscollege.edu', 'asdfgh')
    assert b'Logged in' in rv.data

    with client:
        client.get('/courses/180/grades').status_code == 200

        response = client.get('/course/180/session/2/grades')
        assert b'Grades for Software Project 2' in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

def test_show_grades(client):
    """Tests that student can veiw grades on a course"""

    with client:

        client.post('/login', data={'email': 'student@stevenscollege.edu', 'password': 'asdfgh'})

        response = client.get('/course/180/session/2/grades')
        print(response.data)
        assert b'24' in response.data
        assert b'good' in response.data

def test_gradeless(client):
    """Tests if submission is missing the grade should be zero"""
    with client:
        client.post('login', data={'email': 'student2@stevenscollege.edu', 'password': '123456789'})

        response = client.get('/course/180/session/2/grades')

        assert b'Logged in' in response.data
        assert b'0' in response.data

@pytest.mark.parametrize(('course_id', 'error'), (
    (111, 403),
    (58, 404)
))

def test_grade_error_codes(client, course_id, error):
    """Checks to see if accessing different grade books shows an error"""
    with client:

        client.post('/login', data={'email': 'student2@stevenscollege.edu', 'password': '123456789'})

        response = client.get(f'/course/{course_id}/session/2/grades')

        assert response.status_code == error
