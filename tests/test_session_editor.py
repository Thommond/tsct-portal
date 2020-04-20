from flask import g, session
import pytest
from portal.db import get_db
import os
import tempfile
from tests.test_course_editor import login, logout


def test_edit_session(client):
    """Tests the editSession page with a specific session
    of the course 180 to see if functionallity works"""
    assert client.get('/courses/180/sessions/2/edit').status_code == 302

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    with client:
        client.get('/courses/180/sessions/2/edit').status_code == 200

        response = client.get('/courses/180/sessions/2/edit')
        assert b'Edit Session CSET-180-A' in response.data

        response_2 = client.post('/courses/180/sessions/2/edit', data={ 'editName': 'Software Project 2-A',
        'editTimes': '12:30 is the time', 'editRoom': '105', 'editLocal': 'Greenfield'
        }, follow_redirects=True)
        assert b'Sessions for course Software Project 2' in response_2.data
        assert b'Software Project 2-A' in response_2.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data



def test_create_session(client):
    """Tests access of the createSession page and the
    form dat to see if you can successfully create a session
    in a specific course"""

    assert client.get('/courses/180/sessions/create').status_code == 302

    rv = login(client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    with client:
        response = client.get('courses/180/sessions/create')
        assert response.status_code == 200
        assert b'Create a New Session in Software Project 2'

        response_2 = client.post("/courses/180/sessions/create", data={ 'sessionTitle': 'Software Project 2-C',
        'sessionTimes': '12:30 is the time', 'roomNumber': '105', 'locations': 'Greenfield' },
        follow_redirects=True)
        assert b'Sessions for course Software Project 2' in response_2.data
        assert b'Software Project 2-C' in response_2.data
        assert b'Click the + below to create a new session' in response_2.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data


def test_course_sessions(client):
    """Tests the data on the session Manage page of zach fedors
    Software Project 2 sessions"""

    assert client.get('/courses/180/sessions').status_code == 302

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    with client:
        response = client.get('/courses/180/sessions')
        assert b'<h2>Sessions for course Software Project 2' in response.data
        assert b'<h3>Click the + below to create a new session</h3>' in response.data
        assert b'CSET-180-A' in response.data

        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data

def test_unique_teacher(client):
    """Test to make sure teachers cannot view or edit other teachers courses"""
    assert client.get('courses/180/sessions').status_code == 302


    rv = login(client, 'teacher1@stevenscollege.edu', 'password')
    assert b'Logged in' in rv.data

    with client:
        response = client.get('courses/180/sessions', follow_redirects=True)
        # Ensure that it redirects to index if teacher does not own course
        print(response.data)
        assert b'Course Management' in response.data
        assert b'Home' in response.data

        response_2 = client.get('/courses/180/sessions/create', follow_redirects=True)

        assert b'Course Management' in response_2.data

        response_3 = client.get('/courses/180/sessions/2/edit', follow_redirects=True)

        assert b'Course Management' in response_3.data


        rv = logout(client)
        assert b'TSCT Portal Login' in rv.data
