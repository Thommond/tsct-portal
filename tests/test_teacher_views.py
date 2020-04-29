import pytest
from portal.student_views import view_schedule
from .test_courses import login, logout

def test_all_grades(client):
    # Make sure anonymous users cannot access
    assert client.get('/course/216/session/1/all_grades').status_code == 302
    # Login
    rv = login(client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data
    # Make sure teacher can access
    assert client.get('/course/216/session/1/all_grades').status_code == 403
    # Log out of teacher who should not have access
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

    rv = login(client, 'teacher2@stevenscollege.edu', 'PASSWORD')
    assert b'Logged in' in rv.data
    # should be able  to access
    assert client.get('/course/216/session/1/all_grades').status_code == 200

    response = client.get('/course/216/session/1/all_grades')
    # Making sure students grades are displaying
    assert b'bob phillp' in response.data
    assert b'<td>F</td>' in response.data
