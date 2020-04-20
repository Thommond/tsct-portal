from flask import g, session, url_for
import pytest
from portal.db import get_db
from portal.auth import login, logout
import os
import tempfile


def login(client, email, password):
    """Logs in a user"""
    return client.post("/login", data=dict(
        email=email,
        password=password,

    ), follow_redirects=True)


def logout(client):
    """Logs out a user"""
    return client.get("/logout", follow_redirects=True)


def test_login_logout(client):
    """Make sure login and logout functions work."""

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

    rv = login(
        client, 'teacher@stevenscollege.edu'+ 'x', 'qwerty')
    assert b'Incorrect email or password' in rv.data

    rv = login(client, 'teacher@stevenscollege.edu',
               'qwerty' + 'x')
    assert b'Incorrect email or password' in rv.data


def test_edit(client):
    """Tests the courseEdit page with a specific id of the logged
    in user. Also sees if editing the course forms work"""
    assert client.get('/courses/180/edit').status_code == 302

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    with client:
        assert client.get('/courses/180/edit').status_code == 200

        response = client.get('/courses/180/edit')
        assert b'The courses current information' in response.data

        response2 = client.post('/courses/180/edit', data={'editTitle': 'Software Project 6',
        'editDesc': 'Making a website', 'editCredit': 3}, follow_redirects=True)
        assert b'Software Project 6' in response2.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data

# Test a few faliure edits an feedback a error
@pytest.mark.parametrize(('editTitle', 'editCredit',  'error'),
( ('', '4', b'Title of course is required'),
('wow_a_title','', b'Credit amount is required')
))

def test_edit_function_errors(client, editTitle, editCredit, error):

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    response = client.post('/courses/180/edit', data={'editTitle':editTitle, 'editCredit': editCredit })

    # Make sure errors display on page
    assert error in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data



def test_create_course(client):
    """Tests access of the courseCreate page
    and tests the forms data to see if creating a course works"""

    assert client.get('/courses/create').status_code == 302

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data


    with client:
        client.get('/courses/create').status_code == 200

        response = client.get('/courses/create')
        assert b'Create a New Course' in response.data

        response_2 = client.post('/courses/create', data={'courseTitle': 'Welding 101',
        'description': 'Learning how to use mig welder', 'courseCredits': 3, 'major_name': 2}, follow_redirects=True)

        assert b'<h4>Welding 101</h4>' in response_2.data
        assert b'<h4>Software Project 2</h4>' in response_2.data
        assert b'Course Management' in response_2.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data




# Test a few cases of creating a course
@pytest.mark.parametrize(('courseTitle', 'courseCredits', 'major_name', 'error'),
( ('title_of_course', '', 3, b'Credit amount is required'),
  ('', '3', 2, b'Title of course is required')
))

def test_edit_function_errors(client, courseTitle, courseCredits, major_name, error):
    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data


    response = client.post('/courses/create', data={'courseTitle':courseTitle, 'courseCredits': courseCredits,'major_name': major_name, 'description': ''})
    # Make sure errors display on page
    assert error in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data



def test_unique_teacher(client):
    """Test to make sure teachers cannot view or edit other teachers courses"""
    assert client.get('courses/216/edit').status_code == 302


    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    with client:
        response = client.get('courses/216/edit', follow_redirects=True)
        # Ensure that it redirects to index if teacher does not own course
        assert b'Course Management' in response.data
        assert b'Home' in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data


def test_course_manage(client):
    """Tests the data on the page of courseManagement and access of teacher"""

    assert client.get('/courses').status_code == 302

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    with client:
        response = client.get('/courses')
        assert b'<h2>Course Management</h2>' in response.data
        assert b'<h3>Click the + below to create a new course</h3>' in response.data
        assert b'Software Project 2' in response.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data
