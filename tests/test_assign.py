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
     'description': 'testing_description', 'points': 100, 'due_date': '2020-06-22T19:10'}, follow_redirects=True)
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
     'description': description, 'points': points, 'due_date': due_date })

    assert error in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data



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
    assert b'Click the + below to create a new assignment' in response.data
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
     'edit_desc': 'first test', 'edit_points': 90, 'edit_date': '2020-06-22T19:10'},follow_redirects=True)
    assert b'Assignments for CSET-180-A' in response_2.data
    assert b'first portal creation' in response_2.data
    #logout
    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data


@pytest.mark.parametrize(('name', 'description', 'points', 'edit_date', 'error'),(
    ('testing exam', 'enter discription', '', '2020-06-22T19:10', b'Points are numbers only, check your values.'),
    ('', 'enter description', 90, '2020-06-22T19:10', b'Name is required.'),
    ('testing exam again', 'description', 10,"", b'Due Date only allows time data, check your values. Please format the time as such using military time. Year-Month-Day Hour:Minute ex. 2020-06-22 19:10')
    ))

def test_edit_errors(client, name, description, points, edit_date, error):


    rv = login(
     client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    response = client.post('/course/180/session/2/assignment/Edit/1/', data={'edit_name': name,
     'edit_desc': description, 'edit_points': points, 'edit_date': edit_date },follow_redirects = True)
    assert error in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data

#check that only teacher who own a specific session can access specific assignments
def test_teacher(client):
    assert client.get('/course/180/session/2/assignment/Edit/2/').status_code == 302

    rv = login(
        client, 'teacher@stevenscollege.edu', 'qwerty')
    assert b'Logged in' in rv.data

    response = client.get('/course/180/session/2/assignment/Edit/2/',follow_redirects = True)
    assert b'Home' in response.data

    rv = logout(client)
    assert b'TSCT Portal Login' in rv.data
