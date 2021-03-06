import pytest
from portal.student_views import view_schedule
from .test_courses import login, logout

def test_all_grades(client):
    # Make sure anonymous users cannot access
    assert client.get('/course/216/session/1/all_grades').status_code == 302
    # Login
    rv = login(client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data
    # Make sure teacher can not access
    assert client.get('/course/216/session/1/all_grades').status_code == 403
    # Log out of teacher who should not have access
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

    rv = login(client, 'teacher2@stevenscollege.edu', 'PASSWORD')
    assert b'Logged in' in rv.data
    # should be able to access
    assert client.get('/course/216/session/1/all_grades').status_code == 200
    assert client.get('/course/180/session/1/all_grades').status_code == 403
    assert client.get('/course/216/session/2/all_grades').status_code == 403

    response = client.get('/course/216/session/1/all_grades')
    # Making sure students grades are displaying
    assert b'bob phillp' in response.data
    assert b'<td>F</td>' in response.data
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data


def test_assignment_grades(client):
    # Make sure anonymous users cannot access
    assert client.get('/course/180/session/2/assignments/1/grades').status_code == 302
    # login
    rv = login(client, 'teacher2@stevenscollege.edu', 'PASSWORD')
    assert b'Logged in' in rv.data
    # Make sure other teachers don't have access
    assert client.get('/course/180/session/2/assignments/1/grades').status_code == 403
    # Logout of other teacher
    rv = logout(client)
    assert b'TSCT Portal Login'
    # Login as teacher that owns the course
    rv = login(client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data
    # Check that you can get the page
    assert client.get('/course/180/session/2/assignments/1/grades').status_code == 200
    assert client.get('/course/216/session/2/assignments/1/grades').status_code == 403
    assert client.get('/course/216/session/1/assignments/1/grades').status_code == 403
    assert client.get('/course/216/session/2/assignments/2/grades').status_code == 403

    response = client.get('/course/180/session/2/assignments/1/grades')
    # Making sure that students' grades and assignment points display on page
    assert b'bob phillp' in response.data
    assert b'<td>A</td>' in response.data
    assert b'<td>24/25</td>' in response.data
    # Log out
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data
