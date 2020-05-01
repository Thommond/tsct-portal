from flask import g, session, url_for
import pytest
from portal.db import get_db
# from portal.auth import login, logout
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
        assert b"The course's current information" in response.data

        response2 = client.post('/courses/180/edit', data={'editTitle': 'Software Project 6',
        'editDesc': 'Making a website', 'editCredit': 3}, follow_redirects=True)
        assert b'Software Project 6' in response2.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data

# Test a few faliure edits an feedback a error
@pytest.mark.parametrize(('editTitle', 'editCredit',  'error'), (
    ('', '4', b'Title of course is required'),
    ('wow_a_title','', b'Credit amount is required'),
    ('new_title', 'three', b'Credit amount needs to be a number')
))
def test_edit_function_errors(client, editTitle, editCredit, error):

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    response = client.post('/courses/180/edit', data={
        'editTitle':editTitle, 'editCredit': editCredit, 'editDesc': 'New description' })

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

        response_2 = client.post('/courses/create', data={
                'courseNumber': 102,
                'courseTitle': 'Welding Tig',
                'description': 'Learning how to use mig welder',
                'courseCredits': 3,
                'major_name': 2
            }, follow_redirects=True)

        assert b'<h4>Welding Tig</h4>' in response_2.data
        assert b'<h4>Software Project 2</h4>' in response_2.data
        assert b'Course Management' in response_2.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data




# Test a few cases of creating a course
@pytest.mark.parametrize(('courseNumber', 'courseTitle', 'courseCredits', 'major_name', 'error'),
( (123, 'title_of_course', '', 3, b'Credit amount is required'),
  (123, '', '3', 2, b'Title of course is required'),
  (123, 'title_of_course', 3, '', b'Major is required'),
  (123, 'title_of_course', 'credit', 1, b'Credit amount needs to be a number'),
  (123, 'title_of_course', 1, 'cset', b'Major not found'),
  (123, 'title_of_course', 1, 82, b'Major not found'),
  ('hi', 'title_of_course', 1, 1, b'Course number needs to be a number'),
  ('', 'title_of_course', 1, 1, b'Course number is required'),
  (180, 'title_of_course', '3', 1, b'Course Number already exists' ),
  (190, 'Software Project 2', '3', 1, b'Course Name already exists')
))

def test_create_course_validation(client, courseNumber, courseTitle, courseCredits, major_name, error):
    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data


    response = client.post('/courses/create', data={
            'courseNumber': courseNumber,
            'courseTitle': courseTitle,
            'courseCredits': courseCredits,
            'major_name': major_name,
            'description': 'hello'
        })

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
        assert b'403' in response.data
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
        assert b'<h3>Click the link below to create a new course</h3>' in response.data
        assert b'Software Project 2' in response.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data

def test_course_404(client):
    """Ensures that an incorrect course id leads to a 404"""

    with client:
        login(client, 'teacher@stevenscollege.edu', 'qwerty')

        response = client.get('/courses/999/edit')

        assert b'404' in response.data
