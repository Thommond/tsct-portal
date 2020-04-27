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
