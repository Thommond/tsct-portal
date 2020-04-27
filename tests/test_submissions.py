import pytest

def test_submission_list(client):
    """Tests that adding a grade to a student's assignment submission works"""

    response = client.get('/course/180/session/2/assignments/1/submissions')

    assert response.status_code == 302

    with client:

        client.post('/login', data={'email': 'teacher2@stevenscollege.edu', 'password': 'PASSWORD'})

        response = client.get('/course/216/session/1/assignments/2/submissions')

        response.status_code == 200
        assert b'Marisa Kirisame' in response.data
        assert b'bob phillp' in response.data

def test_add_grade(client):
    """Tests that grades can be entered onto submissions"""

    with client:

        client.post('/login', data={'email': 'teacher2@stevenscollege.edu', 'password': 'PASSWORD'})

        response = client.get('/course/216/session/1/assignments/2/submissions/1')
        assert b'Enter feedback' in response.data

        response = client.post('/course/216/session/1/assignments/2/submissions/1',
            data={ 'grade': 25, 'feedback': 'good' })

        assert b'25' in response.data
        assert b'good' in response.data
        assert b'Grade Entered' in response.data


@pytest.mark.parametrize(('email', 'password', 'route', 'error'), (
    ('teacher@stevenscollege.edu', 'qwerty', '1/assignments/2/submissions', 403),
    ('teacher@stevenscollege.edu', 'qwerty', '1/assignments/2/submissions/1', 403),
    ('student@stevenscollege.edu', 'asdfgh', '1/assignments/2/submissions', 403),
    ('student@stevenscollege.edu', 'asdfgh', '1/assignments/2/submissions/1', 403),
    ('teacher2@stevenscollege.edu', 'PASSWORD', '1/assignments/2/submissions/99', 404),
    ('teacher2@stevenscollege.edu', 'PASSWORD', '1/assignments/99/submissions/99', 404),
    ('teacher2@stevenscollege.edu', 'PASSWORD', '1/assignments/1/submissions', 403),
    ('teacher2@stevenscollege.edu', 'PASSWORD', '1/assignments/1/submissions/1', 403),
    ('teacher2@stevenscollege.edu', 'PASSWORD', '1/assignments/2/submissions/2', 403),
    ('teacher2@stevenscollege.edu', 'PASSWORD', '99/assignments/2/submissions', 404),
    ('teacher2@stevenscollege.edu', 'PASSWORD', '1/assignments/99/submissions', 404)
))
def test_submission_error_codes(client, email, password, route, error):
    """Checks various scenarios that should fail with the correct error code"""
    with client:

        client.post('/login', data={'email': email, 'password': password})

        response = client.get(f'/course/216/session/{route}')

        assert response.status_code == error

def test_submission_input_validation(client):
    """Tests that the input validation on grades works correctly"""
    with client:

        client.post('/login', data={'email': 'teacher2@stevenscollege.edu', 'password': 'PASSWORD'})

        response = client.post('/course/216/session/1/assignments/2/submissions/1',
            data={ 'grade': 'A', 'feedback': 'good' })

        assert b'Grade needs to be a number' in response.data
