from flask import g, session, url_for
import pytest
from portal.db import get_db
from .test_courses import login, logout
import os
import tempfile

def test_assign_create(client):

    #test that assign_create exists
    assert client.get('/course/180/session/2/assignment/create/').status_code == 302


    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    #test getting the assign created
    assert client.get('/course/180/session/2/assignment/create/').status_code == 200
    #check response data for response assign create
    response = client.get('/course/180/session/2/assignment/create/')
    assert b'Create a New Assignment for CSET-180-A' in response.data
    assert b'Name' in response.data
    #make post request to test functionality of test created
    #test redirection to assign manage
    response_2 = client.post('/course/180/session/2/assignment/create/', data={'name': 'portal creation',
     'description': 'testing_description', 'points': 100, 'due_date': '2020-06-22T19:10',
     'type': 'standard'}, follow_redirects=True)
    #in assign manage data make sure assign manage is there
    assert b'Assignments for CSET-180-A' in response_2.data
    assert b'portal creation' in response_2.data


    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data


@pytest.mark.parametrize(('name', 'description', 'points', 'due_date', 'error'), (
    ('testing exam', 'enter discription', '', '2020-06-22T19:10', b'Points are numbers only, check your values.'),
    ('', 'enter description', 90, '2020-06-22T19:10', b'Name is required.'),
    ('testing exam again', 'description', 10,"", b'Due Date only allows time data, check your values. Please format the time as such using military time. Year-Month-Day Hour:Minute ex. 2020-06-22 19:10')
    ))

def test_create_errors(client, name, description, points, due_date, error):

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data


    response = client.post('/course/180/session/2/assignment/create/', data={'name': name,
     'description': description, 'points': points, 'due_date': due_date , 'type': 'standard'})

    assert error in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data


@pytest.mark.parametrize(('type'), (
    ('standard'),
    ('sadf8ewfhc'),
    ('upload')
))
def test_types(client, type):

    with client:
        # Log in as the teacher to create the assignment
        login(client, 'teacher2@stevenscollege.edu', 'PASSWORD')

        client.post('/course/216/session/1/assignment/create/', data={
            'name': 'test',
            'description': 'this is a test assignment',
            'points': 100,
            'due_date': '2020-05-29T12:00',
            'type': type
        })
        logout(client)

        # Log in as the student to check for a submit button
        login(client, 'student2@stevenscollege.edu', '123456789')

        response = client.get('/course/216/session/1/assignment_details/3')
        # If the assignment is upload type, there should be a submit button
        # on the page.  If not, then there shouldn't be

        if type == 'upload':
            assert b'Submit' in response.data
        else:
            assert b'Submit' not in response.data


def test_assign_manage(client):

    #test getting assignment manage
    assert client.get('/course/180/session/2/assignments/').status_code == 302
    #can we login
    rv = login(
     client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data
     #can we access after login
    assert client.get('/course/180/session/2/assignments/').status_code == 200
     #test data of the page
    response = client.get('/course/180/session/2/assignments/')
    assert b'Assignments for CSET-180-A' in response.data
    assert b'Add Assignment' in response.data
     #logout
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

def test_assign_edit(client):

    #test getting assignemnt edit
    assert client.get('/course/180/session/2/assignment/Edit/1/').status_code == 302
    rv = login(
     client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data
    #test the assign edit after login
    assert client.get('/course/180/session/2/assignment/Edit/1/').status_code == 200
    #get response data on page
    response = client.get('/course/180/session/2/assignment/Edit/1/')
    #getting data on edit page
    assert b'Name' in response.data
    assert b'Description' in response.data
    assert b'Points' in response.data
    #editing the page with request
    response_2 = client.post('/course/180/session/2/assignment/Edit/1/', data={'edit_name': 'first portal creation',
     'edit_desc': 'first test', 'edit_points': 90, 'edit_date': '2020-06-22T19:10',
     'edit_type': 'upload'}, follow_redirects=True)
    assert b'Assignments for CSET-180-A' in response_2.data
    assert b'first portal creation' in response_2.data
    #logout
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

# Test data to ensure assign edit post request faliure
@pytest.mark.parametrize(('name', 'description', 'points', 'edit_date', 'error'),(
    ('testing exam', 'enter discription', '', '2020-06-22T19:10', b'Points are numbers only, check your values.'),
    ('', 'enter description', 90, '2020-06-22T19:10', b'Name is required.'),
    ('testing exam again', 'description', 10,"", b'Please format date &amp; time as')
    ))

def test_edit_errors(client, name, description, points, edit_date, error):
    """Makes sure the proper errors are
    flashed for a request in edit assign"""

    rv = login(
     client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    response = client.post('/course/180/session/2/assignment/Edit/1/', data={'edit_name': name,
     'edit_desc': description, 'edit_points': points, 'edit_date': edit_date,
     'edit_type': 'standard'}, follow_redirects = True)

    assert error in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data


def test_teacher(client):
    """check that only teacher who own a specific
    session can access specific assignments"""

    assert client.get('/course/180/session/2/assignment/Edit/2/').status_code == 302

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    response = client.get('/course/180/session/2/assignment/Edit/2/',follow_redirects = True)
    assert b'Home' in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data
