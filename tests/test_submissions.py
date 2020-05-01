import pytest
import io

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

def test_submission_form(client):
    """Tests the page that students use to submit assignments"""
    response = client.get('/course/216/session/1/assignment/2/submit')
    assert response.status_code == 302

    with client:
        client.post('/login', data={'email': 'student2@stevenscollege.edu', 'password': '123456789'})
        # Check that the submission form exists
        response = client.get('/course/216/session/1/assignment/2/submit')
        assert response.status_code == 200

        assert b'Upload File' in response.data
        assert b'Submit Assignment' in response.data

def test_file_validation(client):

    with client:
        client.post('/login', data={'email': 'student2@stevenscollege.edu', 'password': '123456789'})

        # Submitting with no file selected should return an error
        response = client.post('/course/216/session/1/assignment/2/submit',
            data={'file': ''})
        assert b'File not selected' in response.data

        # A file with no title should count as not selected as well
        response = client.post('/course/216/session/1/assignment/2/submit',
            data={'file': (io.BytesIO(b""), '')})
        assert b'File not selected' in response.data

        response = client.post('/course/216/session/1/assignment/2/submit',
            data={'file': (io.BytesIO(b"This is a bad file"), 'malware.exe')})
        assert b'File extension not allowed' in response.data

def test_file_upload(client):

    # Anonymous user should get redirected
    response = client.post('/course/216/session/1/assignment/2/submit')

    assert response.status_code == 302

    with client:
        client.post('/login', data={'email': 'student2@stevenscollege.edu', 'password': '123456789'})
        # As a student, upload a file
        response = client.post('/course/216/session/1/assignment/2/submit',
            data={'file': (io.BytesIO(b"This is a test file"), 'test.txt')})
        assert response.status_code == 302

        # Check that an uploaded file appears in the file system
        file = open('portal/uploads/1-test.txt')
        assert 'This is a test file' in file.read()
        file.close()

        # Check that a different file uploaded with the same name doesn't
        # overwrite the original file

        client.post('/login', data={'email': 'student@stevenscollege.edu', 'password': 'asdfgh'})

        response = client.post('/course/216/session/1/assignment/2/submit',
            data={'file': (io.BytesIO(b"Hello World"), 'test.txt')})

        file = open('portal/uploads/1-test.txt')
        assert 'This is a test file' in file.read()
        file.close()

        file = open('portal/uploads/3-test.txt')
        assert 'Hello World' in file.read()
        file.close()



@pytest.mark.parametrize(('url', 'error'), (
    ('/course/216/session/1/assignment/99/submit', 404),
    ('/course/216/session/99/assignment/2/submit', 404),
    ('/course/999/session/1/assignment/2/submit', 404),
    ('/course/216/session/1/assignment/1/submit', 403),
    ('/course/216/session/2/assignment/2/submit', 403),
    ('/course/180/session/2/assignment/1/submit', 403)
))
def test_file_upload_redirects(client, url, error):

    with client:
        client.post('/login', data={'email': 'student2@stevenscollege.edu', 'password': '123456789'})

        response = client.get(url)

        assert response.status_code == error
